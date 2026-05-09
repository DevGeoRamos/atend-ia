# ============================================================
# AtendIA v3 — Módulo do Agente de IA
# Segurança reforçada: validação, sanitização, rate limiting
# ============================================================

import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, ANALYSIS_TEMPLATE, FALLBACK_CONTEXT

load_dotenv()


def inicializar_cliente() -> genai.GenerativeModel:
    """Inicializa o cliente do Gemini com configurações otimizadas."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Chave de API não encontrada.")

    genai.configure(api_key=api_key)

    generation_config = genai.GenerationConfig(
        temperature=0.3,
        top_p=0.8,
        top_k=40,
        max_output_tokens=1024,
    )

    # Configuração de segurança — bloqueia conteúdo perigoso
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT,
        safety_settings=safety_settings,
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
    Inclui sanitização de entrada e validação de saída.
    """
    if not ticket or not ticket.strip():
        return {"erro": "Mensagem vazia."}

    if model is None:
        model = inicializar_cliente()

    # Monta o prompt
    if empresa != "Não informado" or segmento != "Não informado":
        prompt = ANALYSIS_TEMPLATE.format(
            segmento=segmento, empresa=empresa, ticket=ticket.strip(),
        )
    else:
        prompt = FALLBACK_CONTEXT.format(ticket=ticket.strip())

    try:
        response = model.generate_content(prompt)
        texto = response.text.strip()

        # Remove markdown wrapping
        texto = texto.replace("```json", "").replace("```", "").strip()

        resultado = json.loads(texto)

        # Validação: garante que campos obrigatórios existem
        campos_obrigatorios = ["sentimento", "urgencia", "categoria", "resposta_sugerida"]
        for campo in campos_obrigatorios:
            if campo not in resultado:
                resultado[campo] = "Não identificado" if campo != "urgencia" else 3

        # Validação: urgência deve ser 1-5
        if not isinstance(resultado.get("urgencia"), int) or resultado["urgencia"] not in range(1, 6):
            resultado["urgencia"] = 3

        return resultado

    except json.JSONDecodeError:
        return {"erro": "Erro ao processar resposta da IA. Tente novamente."}
    except Exception as e:
        erro_str = str(e).lower()
        if "quota" in erro_str or "rate" in erro_str:
            return {"erro": "Limite de requisições da API atingido. Aguarde alguns minutos."}
        elif "api_key" in erro_str or "invalid" in erro_str:
            return {"erro": "Chave de API inválida. Verifique a configuração."}
        else:
            return {"erro": f"Erro inesperado: {str(e)[:100]}"}
