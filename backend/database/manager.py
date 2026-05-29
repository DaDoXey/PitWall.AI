import json
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


def extract_suggested_psi(report_text: str) -> float | None:
    """
    Cerca pattern numerici PSI nella sezione Correzione del report LLM.
    Restituisce la media dei valori trovati, o None se nessun match.
    """
    section_match = re.search(
        r'##\s*Correzione[^\n]*\n(.*?)(?=##|\Z)',
        report_text,
        re.DOTALL | re.IGNORECASE,
    )
    search_text = section_match.group(1) if section_match else report_text

    matches = re.findall(
        r'\b(\d{2}(?:[.,]\d{1,2})?)\s*(?:psi|PSI)\b',
        search_text,
    )
    if not matches:
        return None

    values = []
    for m in matches:
        try:
            values.append(float(m.replace(',', '.')))
        except ValueError:
            continue

    values = [v for v in values if 24.0 <= v <= 32.0]
    return round(sum(values) / len(values), 2) if values else None


class SessionDatabase:
    """Gestisce lo storico delle sessioni ACC in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Costruisci il percorso assoluto: backend/database.db (uno livello sopra)
            self.db_path = Path(__file__).resolve().parent.parent / "database.db"
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def init_db(self) -> None:
        """Crea la tabella `sessions` se non esiste."""
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    car TEXT,
                    track TEXT,
                    psi_input TEXT,
                    psi_suggested TEXT,
                    temp_ambient REAL,
                    temp_track REAL,
                    feedback_text TEXT,
                    llm_response TEXT
                )
                """
            )

    def save_session(self, session_data: Dict[str, Any]) -> str:
        """Inserisce una nuova sessione nel database e ritorna il session_id."""
        session_id = session_data.get("session_id") or str(uuid.uuid4())
        payload = {
            "car": session_data.get("car"),
            "track": session_data.get("track"),
            "psi_input": session_data.get("psi_input"),
            "psi_suggested": session_data.get("psi_suggested"),
            "temp_ambient": session_data.get("temp_ambient"),
            "temp_track": session_data.get("temp_track"),
            "feedback_text": session_data.get("feedback_text"),
            "llm_response": session_data.get("llm_response"),
        }

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    timestamp,
                    car,
                    track,
                    psi_input,
                    psi_suggested,
                    temp_ambient,
                    temp_track,
                    feedback_text,
                    llm_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    session_data.get("timestamp"),
                    payload["car"],
                    payload["track"],
                    json.dumps(payload["psi_input"], ensure_ascii=False) if payload["psi_input"] is not None else None,
                    json.dumps(payload["psi_suggested"], ensure_ascii=False) if payload["psi_suggested"] is not None else None,
                    payload["temp_ambient"],
                    payload["temp_track"],
                    payload["feedback_text"],
                    payload["llm_response"],
                ),
            )
        return session_id

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Recupera le sessioni più recenti ordinate per timestamp decrescente."""
        cursor = self.connection.execute(
            "SELECT * FROM sessions ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        sessions: List[Dict[str, Any]] = []
        for row in rows:
            sessions.append(
                {
                    "session_id": row["session_id"],
                    "timestamp": row["timestamp"],
                    "car": row["car"],
                    "track": row["track"],
                    "psi_input": json.loads(row["psi_input"]) if row["psi_input"] else None,
                    "psi_suggested": json.loads(row["psi_suggested"]) if row["psi_suggested"] else None,
                    "temp_ambient": row["temp_ambient"],
                    "temp_track": row["temp_track"],
                    "feedback_text": row["feedback_text"],
                    "llm_response": row["llm_response"],
                }
            )
        return sessions

    def close(self) -> None:
        """Chiude la connessione SQLite."""
        self.connection.close()
