import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv


class ClaudeEngine:
    MODEL = "claude-opus-4-7"
    ENDPOINT = "https://api.anthropic.com/v1/messages"
    DEFAULT_API_VERSION = "2023-06-01"

    def __init__(self, system_prompt_path: Optional[str] = None):
        root = Path(__file__).resolve().parents[2]
        self.system_prompt_path = Path(system_prompt_path or root / "backend" / "prompts" / "system_prompt.txt")
        self._load_prompt()
        load_dotenv(root / ".env")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Variabile ANTHROPIC_API_KEY non trovata. Inseriscila in .env o nell'ambiente."
            )
        self.api_version = self._normalize_api_version(
            os.getenv("ANTHROPIC_API_VERSION", self.DEFAULT_API_VERSION)
        )

    def _normalize_api_version(self, version: Optional[str]) -> str:
        if not version:
            return self.DEFAULT_API_VERSION
        normalized = version.strip().strip('"\'')
        return normalized or self.DEFAULT_API_VERSION

    def _build_headers(self, include_version: bool = True) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }
        if include_version:
            headers["Anthropic-Version"] = self.api_version
        return headers

    def _load_prompt(self) -> None:
        if not self.system_prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt di sistema non trovato: {self.system_prompt_path}"
            )
        self.system_prompt = self.system_prompt_path.read_text(encoding="utf-8").strip()

    def _build_prompt(self, session_data: Dict[str, Any], pilot_feedback: str) -> str:
        payload = {
            "session_data": session_data,
            "pilot_feedback": pilot_feedback,
        }
        return (
            "Session Data:\n"
            f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n\n"
            "Human: Fornisci un commento qualitativo e costruttivo basato sui dati forniti. "
            "Non generare numeri di setup non giustificati dai dati."
        )

    def generate_commentary(self, session_data: Dict[str, Any], pilot_feedback: str) -> str:
        user_prompt = self._build_prompt(session_data, pilot_feedback)
        body = {
            "model": self.MODEL,
            "system": self.system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 2500,
            "stop_sequences": ["\nHuman:", "\nAssistant:"],
        }

        response = self._post_with_fallback(body)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            details = response.text
            raise RuntimeError(
                f"Errore chiamata AI: {exc}. Dettagli: {details}"
            ) from exc

        data = response.json()
        assistant_message = data.get("completion") or data.get("response")
        if assistant_message is None:
            content = data.get("content")
            if isinstance(content, list):
                texts = [
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                ]
                assistant_message = "".join(texts).strip()
        if assistant_message is None or assistant_message == "":
            raise RuntimeError(
                f"Risposta AI inattesa: {data}"
            )
        return assistant_message

    def _post_with_fallback(self, body: Dict[str, Any]) -> requests.Response:
        headers = self._build_headers(True)
        response = requests.post(self.ENDPOINT, headers=headers, json=body, timeout=30)
        if response.status_code == 400:
            try:
                error_detail = response.json().get("error", {})
                message = error_detail.get("message", "").lower()
            except (ValueError, AttributeError):
                message = ""
            if "not a valid version" in message and self.api_version != self.DEFAULT_API_VERSION:
                response = requests.post(
                    self.ENDPOINT,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key,
                        "Anthropic-Version": self.DEFAULT_API_VERSION,
                    },
                    json=body,
                    timeout=30,
                )
        return response
