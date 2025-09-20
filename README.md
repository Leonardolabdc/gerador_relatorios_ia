# 📚 Gerador de Relatórios com IA

Uma ferramenta web em **Python** e **Streamlit** que automatiza a criação de relatórios executivos de RH a partir de planilhas de dados (XLSX e CSV).  
O MVP integra uma análise estratégica gerada por IA com armazenamento na nuvem (**AWS S3**) para garantir eficiência, consistência e acesso facilitado.

**Acesse a Página de Apresentação do Projeto:**
[**https://leonardolabdc.github.io/gerador_relatorios_ia/**](https://leonardolabdc.github.io/gerador_relatorios_ia/)

---

## ✅ Funcionalidades

- **Upload Dinâmico**: Aceita planilhas de diferentes formatos (XLSX e CSV).  
- **Análise com IA**: A IA do Google Gemini gera relatórios com uma persona de Analista de Dados de RH Sênior, focando em insights estratégicos.  
- **Armazenamento em Nuvem**: Salva todos os relatórios gerados em um bucket do AWS S3, criando um histórico de relatórios.  
- **Interface Intuitiva**: Permite visualizar, baixar relatórios recentes e acessar um histórico de documentos salvos.  

---

## 🏗️ Estrutura do Projeto

```
gerador-relatorios-ia/
├── .streamlit/
│   └── secrets.toml
├── .venv/
├── desafiocomp.py
├── .gitignore
└── README.md
```

---

## ⚙️ Tecnologias Usadas

- **Python**: Linguagem de programação principal.  
- **Streamlit**: Framework para a interface web.  
- **Google Gemini API**: Análise de dados e geração de texto.  
- **Pandas**: Manipulação de dados das planilhas.  
- **boto3 (AWS SDK)**: Integração com o AWS S3.  

---

## 🚀 Como Usar

### Clone o Projeto:
```bash
git clone https://github.com/seu_usuario/seu_repositorio.git
cd seu_repositorio
```

### Crie e Ative o Ambiente Virtual:
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate    # Windows
```

### Instale as Dependências:
```bash
pip install -r requirements.txt
```

### Configure suas Credenciais:
Crie o arquivo `.streamlit/secrets.toml` com suas chaves de API do Gemini e da AWS, junto com o nome do bucket do S3.

### Execute o Aplicativo:
```bash
streamlit run desafiocomps3.py
```
