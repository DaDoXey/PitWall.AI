import json
import os
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


def backfill_suggested_psi(conn: sqlite3.Connection) -> None:
    """
    Aggiorna i record esistenti che hanno psi_suggested NULL o 'N/A'
    estraendo il valore dal campo llm_response già salvato.
    Eseguire solo una volta all'avvio dell'app per backfill dati storici.
    """
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT session_id, llm_response FROM sessions "
            "WHERE psi_suggested IS NULL OR psi_suggested = '\"N/A\"' OR psi_suggested = 'null'"
        )
        rows = cursor.fetchall()
    except Exception:
        return  # Colonna non esistente o altro errore, skip silenzioso

    updated = 0
    for row in rows:
        session_id = row[0]
        report_text = row[1]
        if not report_text:
            continue

        try:
            psi = extract_suggested_psi(report_text)
            if psi is not None:
                cursor.execute(
                    "UPDATE sessions SET psi_suggested = ? WHERE session_id = ?",
                    (json.dumps(psi), session_id),
                )
                updated += 1
        except Exception:
            continue

    conn.commit()


class SessionDatabase:
    """Gestisce lo storico delle sessioni ACC in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Leggi da .env PITWALL_DB_PATH, altrimenti usa default in root workspace
            env_path = os.getenv("PITWALL_DB_PATH")
            if env_path:
                self.db_path = Path(env_path)
            else:
                # Default: ./pitwall_sessions.db nella root della workspace
                self.db_path = Path(".") / "pitwall_sessions.db"
        
        # Assicura che il percorso sia assoluto
        self.db_path = self.db_path.resolve()
        # check_same_thread=False consente l'uso da più thread (Streamlit requirement)
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=5.0)
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
                    conditions TEXT,
                    temp_ambient REAL,
                    temp_track REAL,
                    psi_input TEXT,
                    psi_suggested TEXT,
                    feedback_text TEXT,
                    llm_response TEXT,
                    csv_present INTEGER DEFAULT 0,
                    screenshot_presente INTEGER DEFAULT 0
                )
                """
            )
            # Migrazione: aggiunge colonna screenshot_presente se mancante
            try:
                self.connection.execute(
                    "ALTER TABLE sessions ADD COLUMN screenshot_presente INTEGER DEFAULT 0"
                )
            except Exception:
                pass

    def save_session(self, session_data: Dict[str, Any]) -> str:
        """Inserisce una nuova sessione nel database e ritorna il session_id."""
        session_id = session_data.get("session_id") or str(uuid.uuid4())
        payload = {
            "car": session_data.get("car"),
            "track": session_data.get("track"),
            "conditions": session_data.get("conditions"),
            "temp_ambient": session_data.get("temp_ambient"),
            "temp_track": session_data.get("temp_track"),
            "psi_input": session_data.get("psi_input"),
            "psi_suggested": session_data.get("psi_suggested"),
            "feedback_text": session_data.get("feedback_text"),
            "llm_response": session_data.get("llm_response"),
            "csv_present": 1 if session_data.get("csv_present") else 0,
            "screenshot_presente": 1 if session_data.get("screenshot_presente") else 0,
        }

        with self.connection:
            self.connection.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    timestamp,
                    car,
                    track,
                    conditions,
                    temp_ambient,
                    temp_track,
                    psi_input,
                    psi_suggested,
                    feedback_text,
                    llm_response,
                    csv_present,
                    screenshot_presente
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    session_data.get("timestamp"),
                    payload["car"],
                    payload["track"],
                    payload["conditions"],
                    payload["temp_ambient"],
                    payload["temp_track"],
                    json.dumps(payload["psi_input"], ensure_ascii=False) if payload["psi_input"] is not None else None,
                    json.dumps(payload["psi_suggested"], ensure_ascii=False) if payload["psi_suggested"] is not None else None,
                    payload["feedback_text"],
                    payload["llm_response"],
                    payload["csv_present"],
                    payload["screenshot_presente"],
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
                    "conditions": row["conditions"],
                    "temp_ambient": row["temp_ambient"],
                    "temp_track": row["temp_track"],
                    "psi_input": json.loads(row["psi_input"]) if row["psi_input"] else None,
                    "psi_suggested": json.loads(row["psi_suggested"]) if row["psi_suggested"] else None,
                    "feedback_text": row["feedback_text"],
                    "llm_response": row["llm_response"],
                    "csv_present": bool(row["csv_present"]),
                    "screenshot_presente": bool(row.get("screenshot_presente", 0)),
                }
            )
        return sessions
    
    def get_sessions_filtered(self, car: Optional[str] = None, track: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera sessioni con filtri opzionali per auto e tracciato."""
        try:
            query = "SELECT * FROM sessions WHERE 1=1"
            params = []

            if car and car != "Tutte":
                query += " AND car = ?"
                params.append(car)

            if track and track != "Tutti":
                query += " AND track = ?"
                params.append(track)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.connection.execute(query, params)
            rows = cursor.fetchall()
            sessions: List[Dict[str, Any]] = []
            for row in rows:
                sessions.append(
                    {
                        "session_id": row["session_id"],
                        "timestamp": row["timestamp"],
                        "car": row["car"],
                        "track": row["track"],
                        "conditions": row.get("conditions"),
                        "temp_ambient": row.get("temp_ambient"),
                        "temp_track": row.get("temp_track"),
                        "psi_input": json.loads(row["psi_input"]) if row.get("psi_input") else None,
                        "psi_suggested": json.loads(row["psi_suggested"]) if row.get("psi_suggested") else None,
                        "feedback_text": row.get("feedback_text"),
                        "llm_response": row.get("llm_response"),
                        "csv_present": bool(row.get("csv_present", 0)),
                        "screenshot_presente": bool(row.get("screenshot_presente", 0)),
                    }
                )
            return sessions
        except Exception:
            return []
    
    def get_unique_cars(self) -> List[str]:
        """Recupera lista di auto uniche nello storico."""
        try:
            cursor = self.connection.execute(
                "SELECT DISTINCT car FROM sessions WHERE car IS NOT NULL ORDER BY car"
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []
    
    def get_unique_tracks(self) -> List[str]:
        """Recupera lista di tracciati unici nello storico."""
        try:
            cursor = self.connection.execute(
                "SELECT DISTINCT track FROM sessions WHERE track IS NOT NULL ORDER BY track"
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def close(self) -> None:
        """Chiude la connessione SQLite."""
        self.connection.close()
