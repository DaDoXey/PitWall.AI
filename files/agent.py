"""
agent.py — PitWall.AI v2
Client LLM con system prompt v4.
Compatibile con il contesto esteso (setup completo + CSV + feedback).
"""

import os
import re
from pathlib import Path

import anthropic
from openai import OpenAI


# ─────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt_v4.txt"
REQUIRED_SECTIONS = ["## Diagnosi", "## Causa Meccanica", "## Correzione Setup", "## Note Aggiuntive"]
MAX_RETRIES = 1


def load_system_prompt() -> str:
    """Carica il system prompt dal file. Fallback su stringa minima se file mancante."""
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return (
            "Sei PitWall.AI, un Race Engineer virtuale per ACC. "
            "Rispondi con 4 sezioni: ## Diagnosi, ## Causa Meccanica Probabile, "
            "## Correzione Setup Consigliata, ## Note Aggiuntive."
        )


def validate_output(response: str) -> bool:
    """
    Verifica che l'output LLM contenga le 4 sezioni obbligatorie.
    """
    return all(section in response for section in REQUIRED_SECTIONS)


def call_claude(user_input: str, api_key: str) -> str:
    """Chiamata a Claude Sonnet (primario)."""
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=load_system_prompt(),
        messages=[{"role": "user", "content": user_input}],
    )
    return message.content[0].text


def call_gpt4o_mini(user_input: str, api_key: str) -> str:
    """Chiamata a GPT-4o mini (fallback)."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1500,
        messages=[
            {"role": "system", "content": load_system_prompt()},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content


def get_ai_response(user_input: str, api_key: str) -> str:
    """
    Ottieni risposta dall'LLM con retry logic e fallback.

    Flusso:
      1. Tenta Claude Sonnet
      2. Se output non valido → retry su Claude
      3. Se ancora non valido → fallback GPT-4o mini
      4. Se tutto fallisce → messaggio di errore utente
    """
    anthropic_key = api_key
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Tentativo 1: Claude Sonnet
    try:
        response = call_claude(user_input, anthropic_key)
        if validate_output(response):
            return response
        # Retry 1
        response = call_claude(user_input, anthropic_key)
        if validate_output(response):
            return response
    except Exception:
        pass

    # Fallback: GPT-4o mini
    if openai_key:
        try:
            response = call_gpt4o_mini(user_input, openai_key)
            if validate_output(response):
                return response
        except Exception:
            pass

    return (
        "⚠️ **Errore nella generazione del consiglio.**\n\n"
        "Il servizio è temporaneamente non disponibile. "
        "Riprova tra qualche istante."
    )
