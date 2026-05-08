# ============================================================
# AtendIA — Módulo do Agente de IA
# Toda a comunicação com a API do Gemini fica aqui.
# Isso permite trocar o modelo de IA no futuro sem
# precisar alterar a interface (main.py).
# ============================================================

import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from app.prompts import SYSTEM_PROMPT, ANALYSIS_TEMPLATE, FALLBACK_CONTEXT

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


def inicializar_cliente() -> genai.GenerativeModel:
    """
    Inicializa e retorna o cliente do Gemini.
    Lança um erro claro se a chave de API não estiver configurada.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Chave de API não encontrada. "
            "Crie um arquivo .env com GEMINI_API_KEY=sua_chave_aqui"
        )

    genai.configure(api_key=api_key)

    # Configurações de geração — ajuste conforme necessário
    generation_config = genai.GenerationConfig(
        temperature=0.3,        # Baixo = respostas mais consistentes e previsíveis
        top_p=0.8,
        top_k=40,
        max_output_tokens=1024,
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  # Rápido e gratuito no plano free
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT,
    )

    return model


def analisar_ticket(
    ticket: str,
    empresa: str = "Não informado",
    segmento: str = "Não informado",
    model: genai.GenerativeModel = None,
) -> dict:
    """
    Analisa um ticket de suporte usando IA.

    Parâmetros:
        ticket   — Texto da mensagem do cliente
        empresa  — Nome da empresa (opcional, melhora personalização)
        segmento — Segmento de atuação (opcional)
        model    — Instância do modelo (reutiliza se já existir)

    Retorna:
        dict com a análise estruturada ou dict de erro
    """
    if not ticket or not ticket.strip():
        return {"erro": "Mensagem vazia. Por favor, insira o texto do ticket."}

    # Inicializa o modelo se não foi passado (primeira chamada)
    if model is None:
        model = inicializar_cliente()

    # Monta o prompt com contexto da empresa se disponível
    if empresa != "Não informado" or segmento != "Não informado":
        prompt = ANALYSIS_TEMPLATE.format(
            segmento=segmento,
            empresa=empresa,
            ticket=ticket.strip(),
        )
    else:
        prompt = FALLBACK_CONTEXT.format(ticket=ticket.strip())

    try:
        response = model.generate_content(prompt)
        texto_resposta = response.text.strip()

        # Remove possíveis blocos de markdown caso o modelo os inclua
        texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()

        # Converte o JSON da resposta para dicionário Python
        resultado = json.loads(texto_resposta)
        return resultado

    except json.JSONDecodeError as e:
        return {
            "erro": f"Erro ao processar resposta da IA. Tente novamente. (Detalhe: {str(e)})"
        }
    except Exception as e:
        return {
            "erro": f"Erro ao conectar com a API. Verifique sua chave. (Detalhe: {str(e)})"
        }


def validar_chave_api() -> tuple[bool, str]:
    """
    Verifica se a chave de API está configurada e funcionando.
    Retorna (True, "OK") ou (False, "mensagem de erro").
    """
    try:
        model = inicializar_cliente()
        # Faz uma chamada mínima para testar a chave
        model.generate_content("Responda apenas: OK")
        return True, "Chave válida e funcionando."
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Chave inválida ou sem acesso: {str(e)}"
