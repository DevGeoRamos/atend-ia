# ============================================================
# AtendIA v3 — Interface Principal (Streamlit)
# ============================================================
# Refatoração: segurança, estética e UX
# Para rodar: streamlit run app/main.py
# ============================================================

import streamlit as st
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import analisar_ticket, inicializar_cliente

# ── Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="AtendIA — Customer Success com IA",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── API Key (automática via Secrets) ──────────────────────────
def carregar_api_key() -> str:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")

API_KEY = carregar_api_key()

# ── Segurança: Limite de uso por sessão ───────────────────────
LIMITE_POR_SESSAO = 30  # máximo de análises por sessão

def verificar_limite() -> bool:
    return st.session_state.get("total_analisados", 0) < LIMITE_POR_SESSAO

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer { visibility: hidden; }

    /* ── Brand header ── */
    .brand-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
        border-radius: 12px;
        padding: 1.8rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .brand-header::before {
        content: '';
        position: absolute; top: 0; right: 0;
        width: 200px; height: 100%;
        background: linear-gradient(135deg, transparent 40%, rgba(124,58,237,0.2) 100%);
    }
    .brand-title {
        font-size: 28px; font-weight: 700;
        color: #fff; margin: 0 0 4px; letter-spacing: -0.01em;
    }
    .brand-sub {
        font-size: 14px; font-weight: 400;
        color: rgba(255,255,255,0.7); margin: 0;
    }
    .brand-badge {
        display: inline-block; margin-top: 10px;
        background: rgba(124,58,237,0.3); color: #c4b5fd;
        font-size: 11px; font-weight: 600;
        padding: 3px 10px; border-radius: 12px;
        letter-spacing: 0.05em;
    }

    /* ── Status badges ── */
    .status-ok {
        display: inline-flex; align-items: center; gap: 6px;
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 8px; padding: 8px 14px;
        font-size: 13px; color: #15803d; font-weight: 500;
    }
    .status-erro {
        display: inline-flex; align-items: center; gap: 6px;
        background: #fef2f2; border: 1px solid #fecaca;
        border-radius: 8px; padding: 8px 14px;
        font-size: 13px; color: #dc2626; font-weight: 500;
    }

    /* ── Sentimento badges ── */
    .badge {
        display: inline-block; padding: 5px 16px;
        border-radius: 20px; font-size: 13px; font-weight: 600;
    }
    .badge-positivo  { background: #dcfce7; color: #15803d; }
    .badge-neutro    { background: #f1f5f9; color: #475569; }
    .badge-negativo  { background: #fee2e2; color: #dc2626; }
    .badge-frustrado { background: #fef9c3; color: #a16207; }
    .badge-critico   { background: #ffe4e6; color: #e11d48; }

    /* ── Resposta box ── */
    .resposta-box {
        background: #fefefe;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #7c3aed;
        border-radius: 0 12px 12px 0;
        padding: 1.4rem 1.6rem;
        font-size: 15px; line-height: 1.8;
        color: #1e293b; white-space: pre-wrap;
        margin: 8px 0;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 11px; font-weight: 700;
        color: #94a3b8; text-transform: uppercase;
        letter-spacing: 0.1em; margin-bottom: 6px;
    }

    /* ── Onboarding card ── */
    .onboarding {
        background: linear-gradient(135deg, #faf5ff 0%, #f0f0ff 100%);
        border: 1px solid #e9e5f5;
        border-radius: 12px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.5rem;
    }
    .onboarding h4 { color: #3730a3; margin: 0 0 8px; font-size: 16px; }
    .onboarding p { color: #6b7280; font-size: 14px; line-height: 1.7; margin: 0; }
    .onboarding ol { color: #6b7280; font-size: 14px; line-height: 2; margin: 8px 0 0; padding-left: 18px; }

    /* ── Metric card ── */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #f0f0f5;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-value { font-size: 24px; font-weight: 700; color: #1e1b4b; }
    .metric-label { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; }

    /* ── Histórico ── */
    .historico-item {
        background: #f8fafc;
        border: 1px solid #f0f0f5;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 6px;
        font-size: 13px;
        transition: background 0.2s;
    }
    .historico-item:hover { background: #f1f5f9; }

    /* ── Disclaimer ── */
    .disclaimer {
        background: #fffbeb; border: 1px solid #fde68a;
        border-radius: 8px; padding: 10px 14px;
        font-size: 12px; color: #92400e; line-height: 1.6;
    }

    /* ── Botão primário ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        border: none !important; border-radius: 10px !important;
        font-weight: 600 !important; padding: 0.7rem 2rem !important;
        transition: all 0.3s !important; color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Text area ── */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-size: 15px !important; line-height: 1.7 !important;
    }
    .stTextArea textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
    }

    /* ── Sidebar ── */
    .sidebar-section {
        background: rgba(0,0,0,0.03);
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
for key, default in {
    "historico": [],
    "model": None,
    "total_analisados": 0,
    "exemplo_selecionado": "",
    "primeiro_uso": True,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Inicializa modelo
if st.session_state.model is None and API_KEY:
    try:
        os.environ["GEMINI_API_KEY"] = API_KEY
        st.session_state.model = inicializar_cliente()
    except Exception:
        pass

# ── Helpers ───────────────────────────────────────────────────
def cor_urgencia(n):
    return {1:"#22c55e",2:"#84cc16",3:"#f59e0b",4:"#f97316",5:"#ef4444"}.get(n,"#94a3b8")

def label_urgencia(n):
    return {
        1:"🟢 Baixa — até 48h", 2:"🟡 Normal — até 24h",
        3:"🟠 Moderada — até 8h", 4:"🔴 Alta — até 2h",
        5:"🚨 Crítica — imediata"
    }.get(n,"?")

def sanitizar_entrada(texto: str) -> str:
    """Remove caracteres potencialmente perigosos e limita tamanho."""
    texto = texto.strip()
    if len(texto) > 3000:
        texto = texto[:3000]
    return texto

def exibir_resultado(resultado: dict):
    if "erro" in resultado:
        st.error(f"❌ {resultado['erro']}")
        return

    sentimento = resultado.get("sentimento", "neutro").lower()
    urgencia   = resultado.get("urgencia", 1)
    categoria  = resultado.get("categoria", "—")
    resumo     = resultado.get("resumo", "")
    resposta   = resultado.get("resposta_sugerida", "")
    tags       = resultado.get("tags", [])
    tom        = resultado.get("tom_recomendado", "cordial")

    st.markdown("---")

    # Métricas em cards visuais
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<p class="section-label">Sentimento</p>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-{sentimento}">{sentimento.capitalize()}</span>', unsafe_allow_html=True)
    with c2:
        st.markdown('<p class="section-label">Urgência</p>', unsafe_allow_html=True)
        st.markdown(label_urgencia(urgencia))
    with c3:
        st.markdown('<p class="section-label">Categoria</p>', unsafe_allow_html=True)
        st.markdown(f"**{categoria}**")
    with c4:
        st.markdown('<p class="section-label">Tom recomendado</p>', unsafe_allow_html=True)
        st.markdown(f"**{tom.capitalize()}**")

    # Barra de urgência
    cor = cor_urgencia(urgencia)
    st.markdown(f"""
    <div style="height:6px;background:#f1f5f9;border-radius:3px;margin:16px 0 24px;">
        <div style="width:{urgencia*20}%;height:100%;background:{cor};border-radius:3px;transition:width .6s ease;"></div>
    </div>""", unsafe_allow_html=True)

    if resumo:
        st.markdown('<p class="section-label">Resumo</p>', unsafe_allow_html=True)
        st.info(f"💡 {resumo}")

    if tags:
        st.markdown('<p class="section-label">Tags internas</p>', unsafe_allow_html=True)
        tag_html = " ".join([
            f'<span style="background:#ede9fe;color:#6d28d9;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:500;margin-right:4px;">{t}</span>'
            for t in tags
        ])
        st.markdown(tag_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">💬 Resposta sugerida</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="resposta-box">{resposta}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.code(resposta, language=None)
    st.caption("☝️ Selecione o texto acima e copie com Ctrl+C")


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🎯 AtendIA")
    st.caption("Assistente de Customer Success com IA")
    st.markdown("---")

    # Status
    if st.session_state.model is not None:
        st.markdown('<div class="status-ok">✅ IA conectada</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-erro">⚠️ API não configurada</div>', unsafe_allow_html=True)
        st.caption("Configure GEMINI_API_KEY nos Secrets.")

    st.markdown("---")

    # Personalização
    st.markdown("**🏢 Personalização**")
    st.caption("Opcional — melhora as respostas.")
    empresa_input  = st.text_input("Empresa", placeholder="Ex: Saúde Total")
    segmento_input = st.selectbox("Segmento", [
        "Não informado", "Planos de Saúde", "SaaS / Software",
        "E-commerce", "Financeiro", "Educação", "Varejo", "Outro",
    ])

    st.markdown("---")

    # Métricas
    st.markdown("**📈 Sessão**")
    mc1, mc2 = st.columns(2)
    mc1.metric("Analisados", st.session_state.total_analisados)
    restantes = LIMITE_POR_SESSAO - st.session_state.total_analisados
    mc2.metric("Restantes", restantes)

    if st.session_state.historico:
        neg = sum(1 for h in st.session_state.historico
                 if h.get("sentimento") in ["negativo","frustrado","critico"])
        total = len(st.session_state.historico)
        if total > 0:
            st.metric("Taxa crítica", f"{round(neg/total*100)}%")

    st.markdown("---")

    # Disclaimer de segurança
    st.markdown("""
    <div class="disclaimer">
        🔒 <strong>Privacidade:</strong> Nenhum dado é armazenado.
        Os tickets são processados em tempo real e descartados
        ao fechar a sessão.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Desenvolvido por [Geovane Ramos](https://linkedin.com/in/geovane-ramos)")
    st.caption("[GitHub](https://github.com/DevGeoRamos/atend-ia)")


# ══════════════════════════════════════════════════════════════
#  ÁREA PRINCIPAL
# ══════════════════════════════════════════════════════════════

# Brand header
st.markdown("""
<div class="brand-header">
    <p class="brand-title">🎯 AtendIA</p>
    <p class="brand-sub">Análise inteligente de tickets para equipes de Customer Success</p>
    <span class="brand-badge">POWERED BY GOOGLE GEMINI</span>
</div>
""", unsafe_allow_html=True)

# Onboarding — só aparece na primeira vez
if st.session_state.primeiro_uso and st.session_state.total_analisados == 0:
    st.markdown("""
    <div class="onboarding">
        <h4>👋 Como usar o AtendIA</h4>
        <ol>
            <li>Cole a mensagem de um cliente no campo abaixo</li>
            <li>Clique em <strong>Analisar Ticket</strong></li>
            <li>Receba: sentimento, urgência, categoria e resposta sugerida</li>
        </ol>
        <p style="margin-top:10px;">💡 <em>Clique nos exemplos abaixo para testar rapidamente.</em></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Análise de Ticket")
st.markdown("Cole a mensagem do cliente para análise completa.")

# Exemplos
with st.expander("💡 Exemplos de tickets para testar"):
    exemplos = {
        "😡 Frustrado com cancelamento": "Estou MUITO insatisfeito com o serviço de vocês! Faz 3 semanas que solicitei o cancelamento do meu plano e até hoje não resolveram. Vou processar a empresa se não resolverem HOJE.",
        "❓ Dúvida sobre plano": "Boa tarde! Gostaria de saber quais são as coberturas do meu plano básico. Preciso realizar um exame de sangue e não sei se está incluso. Obrigado!",
        "⭐ Elogio": "Quero registrar que a atendente Ana foi excepcional! Resolveu meu problema em menos de 10 minutos. Parabéns pelo atendimento!",
        "🚨 Sinistro urgente": "Minha mãe está internada e o hospital está negando o atendimento dizendo que o plano não está ativo. Mas eu paguei a mensalidade! Preciso de ajuda URGENTE, por favor!",
    }
    cols = st.columns(2)
    for i, (nome, texto) in enumerate(exemplos.items()):
        if cols[i % 2].button(nome, key=f"ex_{i}", use_container_width=True):
            st.session_state.exemplo_selecionado = texto
            st.session_state.primeiro_uso = False
            st.rerun()

# Campo de texto
ticket_texto = st.text_area(
    "ticket",
    value=st.session_state.exemplo_selecionado,
    height=150,
    placeholder="Cole aqui a mensagem do cliente...\n\nExemplo: 'Estou tentando remarcar minha consulta há 3 dias e ninguém me responde.'",
    label_visibility="collapsed",
)

# Botões
ca, cb, _ = st.columns([2, 1, 4])
with ca:
    analisar = st.button("🔍 Analisar Ticket", type="primary", use_container_width=True)
with cb:
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state.exemplo_selecionado = ""
        st.rerun()


# ── Processamento ─────────────────────────────────────────────
if analisar:
    if not ticket_texto.strip():
        st.warning("⚠️ Cole uma mensagem para analisar.")
    elif st.session_state.model is None:
        st.error("❌ IA não conectada. Configure a chave de API nos Secrets do Streamlit Cloud.")
    elif not verificar_limite():
        st.error(f"⚠️ Limite de {LIMITE_POR_SESSAO} análises por sessão atingido. Recarregue a página para nova sessão.")
    else:
        # Sanitiza entrada
        ticket_limpo = sanitizar_entrada(ticket_texto)

        if len(ticket_limpo) < 5:
            st.warning("⚠️ Mensagem muito curta para análise.")
        else:
            st.session_state.primeiro_uso = False

            with st.spinner("🤖 Analisando ticket..."):
                resultado = analisar_ticket(
                    ticket=ticket_limpo,
                    empresa=empresa_input or "Não informado",
                    segmento=segmento_input,
                    model=st.session_state.model,
                )

            if "erro" not in resultado:
                st.session_state.historico.append({
                    "horario":    datetime.now().strftime("%H:%M"),
                    "preview":    ticket_limpo[:50] + "..." if len(ticket_limpo) > 50 else ticket_limpo,
                    "sentimento": resultado.get("sentimento", "neutro"),
                    "urgencia":   resultado.get("urgencia", 1),
                })
                st.session_state.total_analisados += 1

            exibir_resultado(resultado)


# ── Histórico ─────────────────────────────────────────────────
if st.session_state.historico:
    st.markdown("---")
    st.markdown("### 📋 Histórico da Sessão")
    st.caption("Dados não persistem — são descartados ao fechar.")

    icones = {"positivo":"🟢","neutro":"⚪","negativo":"🔴","frustrado":"🟡","critico":"🚨"}
    for item in reversed(st.session_state.historico[-10:]):
        ic = icones.get(item["sentimento"], "⚪")
        st.markdown(
            f'<div class="historico-item"><strong>{item["horario"]}</strong> &nbsp;'
            f'{ic} {item["sentimento"].capitalize()} &nbsp;·&nbsp; '
            f'Urgência {item["urgencia"]}/5 &nbsp;·&nbsp; {item["preview"]}</div>',
            unsafe_allow_html=True,
        )
