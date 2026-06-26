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


# ─────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt_v4.txt"
REQUIRED_SECTIONS = ["## Diagnosi", "## Causa Meccanica", "## Correzione Setup", "## Note Aggiuntive"]
MAX_RETRIES = 1


def get_env_var(name: str, default: str = "") -> str:
    """Recupera una variabile da st.secrets (Streamlit Cloud) o os.getenv (locale)."""
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)


MAX_OUTPUT_TOKENS = int(get_env_var("PITWALL_MAX_OUTPUT_TOKENS", "2048"))
MAX_INPUT_TOKENS  = int(get_env_var("PITWALL_MAX_INPUT_TOKENS", "8000"))

LOG_PATH    = get_env_var("PITWALL_PROMPT_LOG_PATH", "PROMPT_LOG.md")
INCIDENT_PATH = get_env_var("PITWALL_INCIDENTS_PATH", "INCIDENTS.md")

CLAUDE_MODEL = get_env_var("LLM_MODEL", "claude-haiku-4-5")



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


def call_claude(user_input: str, api_key: str, model_name: str) -> str:
    """Chiamata a Claude con un modello specifico."""
    client = anthropic.Anthropic(api_key=api_key, base_url="https://api.anthropic.com")
    message = client.messages.create(

        model=model_name,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=load_system_prompt(),
        messages=[{"role": "user", "content": user_input}],
    )
    return message.content[0].text


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
    Ottieni risposta da Claude con retry logic e fallback su altri modelli Anthropic.
    """
    anthropic_key = api_key

    # Controllo dimensione contesto
    context_ok, estimated_tokens = check_and_warn(user_input)
    if not context_ok and show_warning:
        import streamlit as st
        st.warning(
            f"⚠️ Contesto molto grande (~{estimated_tokens} token stimati). "
            "La risposta potrebbe essere più lenta o incompleta. "
            "Prova a ridurre la lunghezza del feedback o del CSV."
        )

    errors = []

    # Lista ordinata di modelli Anthropic da provare in cascata in caso di errori (es. 404)
    models_to_try = [
        CLAUDE_MODEL,              # 1. Modello scelto/configurato da utente
        "claude-haiku-4-5",        # 2. Haiku 4.5 (veloce ed economico)
        "claude-sonnet-4-6",       # 3. Sonnet 4.6 (qualità superiore)
        "claude-3-5-haiku-latest", # 4. Haiku 3.5 (ultimo fallback legacy)
    ]


    # Rimuove duplicati mantenendo l'ordine
    unique_models = []
    for m in models_to_try:
        if m not in unique_models:
            unique_models.append(m)

    for idx, model in enumerate(unique_models):
        try:
            # Primo tentativo con questo modello
            response = call_claude(user_input, anthropic_key, model)
            if validate_output(response):
                log_token_usage(estimated_tokens, MAX_OUTPUT_TOKENS, model, auto, tracciato)
                return response
            
            # Secondo tentativo (retry) con lo stesso modello
            response = call_claude(user_input, anthropic_key, model)
            if validate_output(response):
                log_token_usage(estimated_tokens, MAX_OUTPUT_TOKENS, model, auto, tracciato)
                return response
            
            errors.append(f"Modello {model}: Output generato ma incompleto (sezioni mancanti).")
        except Exception as exc:
            errors.append(f"Modello {model} fallito: {exc}")
            log_incident(f"Errore chiamata Claude ({model}): {exc}")

    log_incident("Tutti i modelli Anthropic hanno fallito.")

    # Restituisce i dettagli dell'errore all'utente per permettere il debug online
    err_details = "\n".join(f"- {err}" for err in errors)
    return (
        "⚠️ **Errore nella generazione del consiglio con Anthropic.**\n\n"
        "Tutti i tentativi con i modelli disponibili sono falliti. Dettagli tecnici:\n\n"
        f"{err_details}\n\n"
        "Verifica che la tua ANTHROPIC_API_KEY sia corretta, attiva e disponga di credito sufficiente."
    )
