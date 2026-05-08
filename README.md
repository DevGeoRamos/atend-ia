# 🎯 AtendIA — Assistente de Customer Success com IA

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-API-orange?style=flat-square&logo=google)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=flat-square)
![License](https://img.shields.io/badge/Licença-MIT-green?style=flat-square)

> Ferramenta inteligente de análise de tickets para equipes de Customer Success — powered by Google Gemini.

---

## 🚀 O que é o AtendIA?

O **AtendIA** é um assistente de IA para equipes de **Customer Success e Suporte ao Cliente**. Ele analisa mensagens de clientes e retorna em segundos:

- 🧠 **Sentimento** do cliente (positivo, neutro, negativo, frustrado, crítico)
- 🚨 **Nível de urgência** de 1 a 5 com tempo de resposta recomendado
- 📂 **Categoria** automática do problema
- 💬 **Resposta sugerida** profissional e empática
- 🏷️ **Tags** para classificação interna
- 🎭 **Tom de comunicação** recomendado

### Por que isso importa?

Uma equipe de atendimento que usa o AtendIA consegue:
- **Priorizar** tickets críticos antes que vire churn
- **Manter qualidade** nas respostas mesmo em momentos de alto volume
- **Reduzir tempo** de primeira resposta
- **Treinar** novos analistas com exemplos de respostas de qualidade

---

## 📸 Screenshots

> *Interface principal — análise de ticket em tempo real*

```
[Screenshot da interface principal aqui]
[Screenshot do resultado com métricas aqui]
[Screenshot do histórico da sessão aqui]
```

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| **Python 3.10+** | Linguagem principal |
| **Streamlit** | Interface web interativa |
| **Google Gemini API** | Modelo de linguagem (LLM) |
| **python-dotenv** | Gerenciamento seguro de variáveis de ambiente |

---

## 📁 Estrutura do Projeto

```
atend-ia/
│
├── app/
│   ├── __init__.py      # Pacote Python
│   ├── main.py          # Interface Streamlit (entrada da aplicação)
│   ├── agent.py         # Lógica de comunicação com a API Gemini
│   └── prompts.py       # Engenharia de Prompts isolada
│
├── .env.example         # Template de variáveis de ambiente
├── .gitignore           # Arquivos ignorados pelo Git
├── requirements.txt     # Dependências do projeto
└── README.md            # Este arquivo
```

**Por que essa estrutura?**
A lógica da IA (`agent.py`) e os prompts (`prompts.py`) ficam **separados** da interface (`main.py`). Isso permite trocar o modelo de IA, a interface ou os prompts de forma independente — padrão de código limpo e escalável.

---

## ⚡ Como Rodar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/DevGeoRamos/atend-ia.git
cd atend-ia
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure sua chave de API

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env e cole sua chave do Google Gemini
# Obtenha gratuitamente em: https://aistudio.google.com
```

Seu `.env` deve ficar assim:
```
GEMINI_API_KEY=AIzaSy...sua_chave_aqui
```

### 5. Rode a aplicação

```bash
streamlit run app/main.py
```

Acesse em: **http://localhost:8501**

---

## 🌐 Deploy Gratuito (Streamlit Cloud)

1. Faça fork deste repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte com seu GitHub e selecione este repositório
4. Em **Advanced Settings > Secrets**, adicione:
```toml
GEMINI_API_KEY = "sua_chave_aqui"
```
5. Clique em **Deploy** — sua aplicação estará online em minutos!

---

## 🔑 Como Obter a Chave de API (Gratuita)

1. Acesse [aistudio.google.com](https://aistudio.google.com)
2. Clique em **"Get API Key"** → **"Create API key"**
3. Copie a chave gerada (começa com `AIza...`)
4. Cole no seu arquivo `.env`

O plano gratuito permite **1.500 requisições/dia** — mais que suficiente para uso individual e testes.

---

## 🗺️ Roadmap

- [x] Análise de sentimento e urgência
- [x] Resposta sugerida com IA
- [x] Histórico da sessão
- [x] Contexto personalizável por empresa
- [ ] Exportação de histórico em CSV
- [ ] Dashboard com métricas acumuladas
- [ ] Suporte a múltiplos idiomas
- [ ] Integração com Zendesk / Freshdesk via API
- [ ] Autenticação de usuários
- [ ] Plano freemium para equipes

---

## 👤 Autor

**Geovane Ramos**
- GitHub: [@DevGeoRamos](https://github.com/DevGeoRamos)
- LinkedIn: [geovane-ramos](https://linkedin.com/in/geovane-ramos)
- Email: geovane_fgd@hotmail.com

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Desenvolvido com IA por <a href="https://github.com/DevGeoRamos">Geovane Ramos</a>
</p>
