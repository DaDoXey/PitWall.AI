"""
agent.py — PitWall.AI v2
Client LLM con system prompt v4.
Compatibile con il contesto esteso (setup completo + CSV + feedback).
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from openai import OpenAI


# ─────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt_v4.txt"
REQUIRED_SECTIONS = ["## Diagnosi", "## Causa Meccanica", "## Correzione Setup", "## Note Aggiuntive"]
MAX_RETRIES = 1

MAX_OUTPUT_TOKENS = int(os.getenv("PITWALL_MAX_OUTPUT_TOKENS", "2048"))
MAX_INPUT_TOKENS  = int(os.getenv("PITWALL_MAX_INPUT_TOKENS", "8000"))

LOG_PATH    = os.getenv("PITWALL_PROMPT_LOG_PATH", "PROMPT_LOG.md")
INCIDENT_PATH = os.getenv("PITWALL_INCIDENTS_PATH", "INCIDENTS.md")


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def check_context_size(context: str) -> tuple[bool, int]:
    estimated = estimate_tokens(context)
    return estimated <= MAX_INPUT_TOKENS, estimated


def log_token_usage(
    input_tokens_estimate: int,
    output_max_tokens: int,
    model: str,
    auto: str,
    tracciato: str,
    log_path: str = LOG_PATH,
) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = (
        "# PitWall.AI — PROMPT LOG\n\n"
        "| Timestamp | Auto | Tracciato | Token In (stima) | Token Out Max | Modello |\n"
        "|---|---|---|---|---|---|\n"
    )
    line = (
        f"| {timestamp} | {auto} | {tracciato} "
        f"| ~{input_tokens_estimate} | {output_max_tokens} | {model} |\n"
    )
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(header)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def log_incident(description: str, incident_path: str = INCIDENT_PATH) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = (
        "# PitWall.AI — INCIDENTS LOG\n\n"
        "| Timestamp | Descrizione |\n"
        "|---|---|\n"
    )
    line = f"| {timestamp} | {description} |\n"
    if not os.path.exists(incident_path):
        with open(incident_path, "w", encoding="utf-8") as f:
            f.write(header)
    with open(incident_path, "a", encoding="utf-8") as f:
        f.write(line)


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
        max_tokens=MAX_OUTPUT_TOKENS,
        system=load_system_prompt(),
        messages=[{"role": "user", "content": user_input}],
    )
    return message.content[0].text


def call_gpt4o_mini(user_input: str, api_key: str) -> str:
    """Chiamata a GPT-4o mini (fallback)."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {"role": "system", "content": load_system_prompt()},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content


def check_and_warn(user_input: str) -> tuple[bool, int]:
    """
    Verifica dimensione contesto e restituisce (ok, estimated_tokens).
    """
    return check_context_size(user_input)


def get_ai_response(
    user_input: str,
    api_key: str,
    auto: str = "",
    tracciato: str = "",
    show_warning: bool = True,
) -> str:
    """
    Ottieni risposta dall'LLM con retry logic e fallback.

    Flusso:
      1. Controlla dimensione contesto
      2. Tenta Claude Sonnet
      3. Se output non valido → retry su Claude
      4. Se ancora non valido → fallback GPT-4o mini
      5. Se tutto fallisce → messaggio di errore utente
      6. Logga utilizzo token su PROMPT_LOG.md
    """
    anthropic_key = api_key
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Controllo dimensione contesto
    context_ok, estimated_tokens = check_and_warn(user_input)
    if not context_ok and show_warning:
        import streamlit as st
        st.warning(
            f"⚠️ Contesto molto grande (~{estimated_tokens} token stimati). "
            "La risposta potrebbe essere più lenta o incompleta. "
            "Prova a ridurre la lunghezza del feedback o del CSV."
        )

    # Tentativo 1: Claude Sonnet
    model_used = "claude-sonnet-4-20250514"
    try:
        response = call_claude(user_input, anthropic_key)
        if validate_output(response):
            log_token_usage(estimated_tokens, MAX_OUTPUT_TOKENS, model_used, auto, tracciato)
            return response
        # Retry 1
        response = call_claude(user_input, anthropic_key)
        if validate_output(response):
            log_token_usage(estimated_tokens, MAX_OUTPUT_TOKENS, model_used, auto, tracciato)
            return response
    except Exception as exc:
        log_incident(f"Errore chiamata Claude: {exc}")

    # Fallback: GPT-4o mini
    model_used = "gpt-4o-mini"
    if openai_key:
        try:
            response = call_gpt4o_mini(user_input, openai_key)
            if validate_output(response):
                log_token_usage(estimated_tokens, MAX_OUTPUT_TOKENS, model_used, auto, tracciato)
                return response
        except Exception as exc:
            log_incident(f"Errore chiamata GPT-4o mini fallback: {exc}")

    log_incident("Tutti i modelli LLM hanno fallito — output di errore restituito all'utente.")
    return (
        "⚠️ **Errore nella generazione del consiglio.**\n\n"
        "Il servizio è temporaneamente non disponibile. "
        "Riprova tra qualche istante."
    )
