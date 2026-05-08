# ============================================================
# AtendIA — Interface Principal (Streamlit)
# ============================================================
# Para rodar localmente: streamlit run app/main.py
# ============================================================

import streamlit as st
import os
import sys
from datetime import datetime

# Garante que o Python encontra os módulos na mesma pasta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import analisar_ticket, inicializar_cliente

# ── Configuração da Página ────────────────────────────────────
st.set_page_config(
    page_title="AtendIA — Customer Success com IA",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Carrega a chave de API automaticamente ────────────────────
# Tenta Streamlit Cloud Secrets primeiro, depois variável de ambiente
def carregar_api_key() -> str:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")

API_KEY = carregar_api_key()

# ── CSS Customizado ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Esconde apenas o menu hamburguer, mantém o toggle da sidebar */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Sidebar mais elegante */
    [data-testid="stSidebar"] {
        background: #0f0f1a;
        border-right: 1px solid #1e1e3a;
    }
    [data-testid="stSidebar"] * { color: #e2e0f0 !important; }
    [data-testid="stSidebar"] .stMetric {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 0.8rem;
        border: 1px solid #2a2a4a;
    }

    /* Botão de análise */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.02em;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(124,58,237,0.4);
    }

    /* Área de texto */
    .stTextArea textarea {
        border-radius: 10px;
        border: 1.5px solid #e2e8f0;
        font-size: 15px;
        line-height: 1.7;
        transition: border-color 0.2s;
    }
    .stTextArea textarea:focus {
        border-color: #7c3aed;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.1);
    }

    /* Cards de resultado */
    .resultado-card {
        background: #fafafa;
        border: 1px solid #f0f0f5;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }

    /* Badge de sentimento */
    .badge {
        display: inline-block;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-positivo  { background: #dcfce7; color: #15803d; }
    .badge-neutro    { background: #f1f5f9; color: #475569; }
    .badge-negativo  { background: #fee2e2; color: #dc2626; }
    .badge-frustrado { background: #fef9c3; color: #a16207; }
    .badge-critico   { background: #ffe4e6; color: #e11d48; }

    /* Resposta sugerida */
    .resposta-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #7c3aed;
        border-radius: 0 10px 10px 0;
        padding: 1.2rem 1.4rem;
        font-size: 15px;
        line-height: 1.8;
        color: #1e293b;
        white-space: pre-wrap;
    }

    /* Label de seção */
    .section-label {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 6px;
    }

    /* Card de status conectado */
    .status-ok {
        display: flex; align-items: center; gap: 8px;
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 8px; padding: 10px 14px;
        font-size: 13px; color: #15803d; font-weight: 500;
    }
    .status-erro {
        display: flex; align-items: center; gap: 8px;
        background: #fef2f2; border: 1px solid #fecaca;
        border-radius: 8px; padding: 10px 14px;
        font-size: 13px; color: #dc2626; font-weight: 500;
    }

    /* Histórico */
    .historico-item {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 6px;
        font-size: 13px;
    }

    /* Header da página */
    .page-header {
        padding: 1rem 0 0.5rem;
        border-bottom: 2px solid #f1f5f9;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Inicialização do Session State ────────────────────────────
if "historico" not in st.session_state:
    st.session_state.historico = []
if "model" not in st.session_state:
    st.session_state.model = None
if "total_analisados" not in st.session_state:
    st.session_state.total_analisados = 0
if "exemplo_selecionado" not in st.session_state:
    st.session_state.exemplo_selecionado = ""

# Inicializa o modelo automaticamente com a chave dos Secrets
if st.session_state.model is None and API_KEY:
    try:
        os.environ["GEMINI_API_KEY"] = API_KEY
        st.session_state.model = inicializar_cliente()
    except Exception:
        pass


# ── Funções Auxiliares ────────────────────────────────────────
def cor_urgencia(nivel: int) -> str:
    return {1: "#22c55e", 2: "#84cc16", 3: "#f59e0b", 4: "#f97316", 5: "#ef4444"}.get(nivel, "#94a3b8")

def label_urgencia(nivel: int) -> str:
    return {
        1: "🟢 Baixa — responder em até 48h",
        2: "🟡 Normal — responder em até 24h",
        3: "🟠 Moderada — responder em até 8h",
        4: "🔴 Alta — responder em até 2h",
        5: "🚨 Crítica — resposta imediata",
    }.get(nivel, "Desconhecida")

def exibir_resultado(resultado: dict):
    if "erro" in resultado:
        st.error(f"❌ {resultado['erro']}")
        return

    sentimento = resultado.get("sentimento", "neutro").lower()
    urgencia   = resultado.get("urgencia", 1)
    categoria  = resultado.get("categoria", "Não classificado")
    resumo     = resultado.get("resumo", "")
    resposta   = resultado.get("resposta_sugerida", "")
    tags       = resultado.get("tags", [])
    tom        = resultado.get("tom_recomendado", "cordial")

    st.markdown("---")
    st.markdown("### 📊 Resultado da Análise")

    # Métricas visuais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<p class="section-label">Sentimento</p>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-{sentimento}">{sentimento.capitalize()}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<p class="section-label">Urgência</p>', unsafe_allow_html=True)
        st.markdown(label_urgencia(urgencia))
    with col3:
        st.markdown('<p class="section-label">Categoria</p>', unsafe_allow_html=True)
        st.markdown(f"**{categoria}**")
    with col4:
        st.markdown('<p class="section-label">Tom Recomendado</p>', unsafe_allow_html=True)
        st.markdown(f"**{tom.capitalize()}**")

    # Barra de urgência visual
    cor = cor_urgencia(urgencia)
    st.markdown(f"""
    <div style="height:6px;background:#f1f5f9;border-radius:3px;margin:12px 0 20px;">
        <div style="width:{urgencia*20}%;height:100%;background:{cor};border-radius:3px;transition:width .5s;"></div>
    </div>""", unsafe_allow_html=True)

    # Resumo
    if resumo:
        st.markdown('<p class="section-label">Resumo do Problema</p>', unsafe_allow_html=True)
        st.info(f"💡 {resumo}")

    # Tags
    if tags:
        st.markdown('<p class="section-label">Tags Internas</p>', unsafe_allow_html=True)
        tag_html = " ".join([
            f'<span style="background:#ede9fe;color:#6d28d9;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:500;margin-right:4px">{t}</span>'
            for t in tags
        ])
        st.markdown(tag_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Resposta sugerida
    st.markdown('<p class="section-label">💬 Resposta Sugerida para o Cliente</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="resposta-box">{resposta}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.code(resposta, language=None)
    st.caption("☝️ Selecione e copie o texto acima para usar")


# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 AtendIA")
    st.markdown("**Assistente de Customer Success com IA**")
    st.markdown("---")

    # Status da conexão — automático, sem pedir chave ao usuário
    if st.session_state.model is not None:
        st.markdown('<div class="status-ok">✅ IA Conectada e pronta</div>', unsafe_allow_html=True)
    elif not API_KEY:
        st.markdown('<div class="status-erro">⚠️ Chave de API não configurada</div>', unsafe_allow_html=True)
        st.caption("Configure GEMINI_API_KEY nos Secrets do Streamlit Cloud.")
    else:
        st.markdown('<div class="status-erro">⚠️ Erro ao conectar — verifique a chave</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Contexto opcional
    st.markdown("### 🏢 Personalização")
    st.caption("Preencha para respostas mais específicas ao seu negócio.")
    empresa_input  = st.text_input("Nome da empresa", placeholder="Ex: Saúde Total")
    segmento_input = st.selectbox("Segmento", [
        "Não informado", "Planos de Saúde", "SaaS / Software",
        "E-commerce", "Financeiro", "Educação", "Varejo", "Outro",
    ])

    st.markdown("---")

    # Métricas da sessão
    st.markdown("### 📈 Sessão Atual")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Analisados", st.session_state.total_analisados)

    if st.session_state.historico:
        negativos = sum(1 for h in st.session_state.historico
                       if h.get("sentimento") in ["negativo", "frustrado", "critico"])
        total = len(st.session_state.historico)
        col_m2.metric("Críticos", f"{round(negativos/total*100)}%")

    st.markdown("---")
    st.markdown("**AtendIA** · Desenvolvido por")
    st.markdown("[Geovane Ramos](https://linkedin.com/in/geovane-ramos)")
    st.markdown("[GitHub](https://github.com/DevGeoRamos/atend-ia) · [LinkedIn](https://linkedin.com/in/geovane-ramos)")


# ── ÁREA PRINCIPAL ────────────────────────────────────────────
st.markdown('<div class="page-header">', unsafe_allow_html=True)
st.markdown("## Análise de Ticket")
st.markdown("Cole abaixo a mensagem do cliente para receber análise completa com IA.")
st.markdown('</div>', unsafe_allow_html=True)

# Exemplos rápidos
with st.expander("💡 Ver exemplos de tickets para testar"):
    exemplos = {
        "Cliente frustrado com cancelamento": "Estou MUITO insatisfeito com o serviço de vocês! Faz 3 semanas que solicitei o cancelamento do meu plano e até hoje não resolveram. Vou processar a empresa se não resolverem HOJE.",
        "Dúvida simples sobre plano":         "Boa tarde! Gostaria de saber quais são as coberturas do meu plano básico. Preciso realizar um exame de sangue e não sei se está incluso.",
        "Elogio ao atendimento":              "Quero registrar que a atendente Ana foi excepcional! Resolveu meu problema em menos de 10 minutos. Continuem assim!",
        "Problema urgente de sinistro":       "Minha mãe está internada e o hospital está negando o atendimento dizendo que o plano não está ativo. Mas eu paguei a mensalidade! Preciso de ajuda URGENTE.",
    }
    cols = st.columns(2)
    for i, (nome, texto) in enumerate(exemplos.items()):
        if cols[i % 2].button(f"📝 {nome}", key=f"ex_{i}"):
            st.session_state.exemplo_selecionado = texto
            st.rerun()

# Campo de texto
ticket_texto = st.text_area(
    "Mensagem do cliente",
    value=st.session_state.exemplo_selecionado,
    height=160,
    placeholder="Cole aqui a mensagem do cliente...",
    label_visibility="collapsed",
)

# Botões
col_a, col_b, col_c = st.columns([2, 1, 4])
with col_a:
    analisar = st.button("🔍 Analisar Ticket", type="primary", use_container_width=True)
with col_b:
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state.exemplo_selecionado = ""
        st.rerun()

# ── Processamento ─────────────────────────────────────────────
if analisar:
    if not ticket_texto.strip():
        st.warning("⚠️ Digite ou cole uma mensagem para analisar.")
    elif st.session_state.model is None:
        st.error("❌ IA não conectada. Verifique a configuração da chave de API.")
    else:
        with st.spinner("🤖 AtendIA está analisando..."):
            resultado = analisar_ticket(
                ticket=ticket_texto,
                empresa=empresa_input or "Não informado",
                segmento=segmento_input,
                model=st.session_state.model,
            )

        if "erro" not in resultado:
            st.session_state.historico.append({
                "horario":    datetime.now().strftime("%H:%M"),
                "preview":    ticket_texto[:55] + "..." if len(ticket_texto) > 55 else ticket_texto,
                "sentimento": resultado.get("sentimento", "neutro"),
                "urgencia":   resultado.get("urgencia", 1),
            })
            st.session_state.total_analisados += 1

        exibir_resultado(resultado)

# ── Histórico ─────────────────────────────────────────────────
if st.session_state.historico:
    st.markdown("---")
    st.markdown("### 📋 Histórico desta Sessão")
    st.caption("Os tickets não são armazenados — apenas durante esta sessão.")

    icones = {"positivo": "🟢", "neutro": "⚪", "negativo": "🔴", "frustrado": "🟡", "critico": "🚨"}
    for item in reversed(st.session_state.historico[-10:]):
        icone = icones.get(item["sentimento"], "⚪")
        st.markdown(
            f'<div class="historico-item"><strong>{item["horario"]}</strong> &nbsp;'
            f'{icone} {item["sentimento"].capitalize()} &nbsp;·&nbsp; '
            f'Urgência {item["urgencia"]}/5 &nbsp;·&nbsp; {item["preview"]}</div>',
            unsafe_allow_html=True,
        )
