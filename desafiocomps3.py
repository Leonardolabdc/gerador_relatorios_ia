import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import base64
import re
import datetime
import json
import boto3

# --- Configurações da Aplicação ---
st.set_page_config(
    page_title="Gerador de Relatórios (Gemini)",
    layout="wide"
)

# Título e descrição do app
st.title("Gerador de Relatórios em HTML com Gemini")
st.write("Faça o upload de uma planilha XLSX ou CSV para gerar um relatório com IA.")

# --- Autenticação da API ---
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except KeyError:
    st.error("Chave da API do Gemini não encontrada. Por favor, adicione sua chave ao arquivo '.streamlit/secrets.toml'.")
    st.stop()
    
# Inicializa o modelo do Gemini
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro ao inicializar o modelo Gemini. Verifique sua chave de API. Erro: {e}")
    st.stop()

# --- Funções do Aplicativo ---

# Função para fazer upload para o S3
def upload_to_s3(file_content, filename, bucket_name):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
        )
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=file_content,
            ContentType='text/html'
        )
        s3_url = f"https://{bucket_name}.s3.sa-east-1.amazonaws.com/{filename}"
        return s3_url
    except Exception as e:
        st.error(f"Erro ao fazer upload para o S3: {e}")
        return None

def generate_report(df, original_filename):
    """Gera um relatório HTML a partir dos dados do DataFrame usando a API do Gemini."""
    
    df_string_para_analise = df.to_markdown(index=False)
    
    prompt = f"""
  Você é um analista de dados de RH sênior. Sua tarefa é analisar os dados de uma planilha e retornar um objeto JSON com um relatório profissional e padronizado.

    Estrutura do JSON:
    {{
        "titulo": "string com o título do relatório",
        "sumario_executivo": "string com HTML para um resumo de alto nível com as principais descobertas, elaborando em pelo menos dois parágrafos.",
        "analise_insights": "string com HTML para uma análise detalhada das principais tendências, correlações ou anomalias, elaborando em pelo menos três parágrafos.",
        "recomendacoes": "string com HTML para sugestões práticas e acionáveis, em formato de lista com pelo menos quatro itens."
    }}

    Instruções e Guardrails:
    1.  O output deve ser um único objeto JSON válido. **Não inclua nenhum texto ou formatação fora do JSON**.
    2.  Os valores das chaves devem ser strings que podem conter tags HTML como <p>, <ul> e <li>.
    3.  A análise deve ser de alto nível, focada em insights estratégicos que seriam úteis para um executivo.
    4.  Não inclua dados brutos, gráficos ou blocos de código.
    5.  O título deve ser relevante e profissional.
    6.  O JSON deve começar com '{{' e terminar com '}}'.
    
    Dados da planilha para análise:
    {df_string_para_analise}
    """
    
    with st.spinner("Gerando a análise com IA..."):
        try:
            response = model.generate_content(prompt)
            report_json_string = response.text
            
            report_json_string = re.sub(r'```json|```', '', report_json_string).strip()

            report_data = json.loads(report_json_string)

            df_html_completo = df.to_html(classes="table table-striped table-hover", index=False)
            
            final_report_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Relatório de Produtividade</title>
                <style>
                    body {{ background-color: white !important; color: black !important; }}
                    h1, h2, h3, h4, h5, h6, p, th, td {{ color: black !important; }}
                    table {{ width: 100%; border-collapse: collapse; font-family: sans-serif; }}
                    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>{report_data.get('titulo', 'Relatório de Análise')} - {original_filename}</h1>
                <h2>Sumário Executivo</h2>
                {report_data.get('sumario_executivo', '<p>Não foi possível gerar o sumário executivo.</p>')}
                <h2>Análise e Insights</h2>
                {report_data.get('analise_insights', '<p>Não foi possível gerar a análise.</p>')}
                <h2>Recomendações</h2>
                {report_data.get('recomendacoes', '<p>Não foi possível gerar as recomendações.</p>')}
                <br><h3>Dados Brutos</h3><p>A tabela abaixo contém todos os dados completos da planilha.</p>
                {df_html_completo}
            </body>
            </html>
            """
            return final_report_html
        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o relatório. Verifique o formato da resposta da IA. Erro: {e}")
            return None


# --- Interface do Usuário ---
# ATUALIZAÇÃO: Tradução do file uploader com CSS mais robusto
st.html("""
<style>
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] label {
        display: none;
    }
    [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInstructions"] > div::before {
        content: "Arraste e solte o arquivo aqui";
        display: block;
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-bottom: 5px;
    }
    [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInstructions"] button {
        content: "Procurar arquivos";
    }
</style>
""")

uploaded_file = st.file_uploader("Escolha um arquivo XLSX ou CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    
        st.success("Arquivo carregado com sucesso!")
        st.subheader("Pré-visualização dos Dados")
        st.dataframe(df.head())

        if st.button("Gerar Relatório em HTML"):
            report_html = generate_report(df, uploaded_file.name)
            
            if report_html:
                st.subheader("Relatório Gerado")
                
                bucket_name = st.secrets["S3_BUCKET_NAME"]
                file_base_name = os.path.splitext(uploaded_file.name)[0]
                clean_name = file_base_name.replace(" ", "_").lower()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                s3_filename = f"{clean_name}_{timestamp}.html"
                
                s3_url = upload_to_s3(report_html, s3_filename, bucket_name)
                
                if s3_url:
                    st.success(f"Relatório salvo com sucesso no S3. URL: {s3_url}")
                    st.markdown(f'<a href="{s3_url}" target="_blank">Visualizar Relatório no S3</a>', unsafe_allow_html=True)
                
                st.download_button(
                    label="Baixar Cópia Local",
                    data=report_html,
                    file_name=f"{clean_name}_{timestamp}.html",
                    mime="text/html"
                )

                st.info("O link acima permite que você acesse o relatório hospedado. O botão abaixo baixa uma cópia local.")
                
                with st.expander("Ver Análise e Dados Completos"):
                    st.components.v1.html(report_html, height=600, scrolling=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo. Verifique se é um arquivo válido. Erro: {e}")

# --- Nova Seção: Histórico de Relatórios ---
st.markdown("---")
st.subheader("Histórico de Relatórios (S3)")
st.write("Aqui, você pode ver e baixar todos os relatórios salvos no S3.")

bucket_name = st.secrets.get("S3_BUCKET_NAME")
if bucket_name:
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
        )
        s3_objects = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in s3_objects:
            relatorios_salvos = sorted([obj['Key'] for obj in s3_objects['Contents']], reverse=True)
            
            selected_file = st.selectbox(
                "Selecione um relatório:",
                options=relatorios_salvos,
                index=0
            )

            if selected_file:
                st.markdown(f'<a href="https://{bucket_name}.s3.sa-east-1.amazonaws.com/{selected_file}" target="_blank">Visualizar no S3</a>', unsafe_allow_html=True)
                
                response = s3.get_object(Bucket=bucket_name, Key=selected_file)
                file_content = response['Body'].read().decode('utf-8')
                
                st.download_button(
                    label=f"Baixar {selected_file}",
                    data=file_content,
                    file_name=selected_file,
                    mime="text/html"
                )
        else:
            st.info("Nenhum relatório foi encontrado no seu bucket S3.")
    
    except Exception as e:
        st.error(f"Erro ao conectar com o S3 ou listar arquivos: {e}. Verifique suas credenciais.")
else:
    st.info("Por favor, configure o nome do seu bucket no arquivo '.streamlit/secrets.toml'.")