#!/usr/bin/env python3
"""PreToolUse guard di PitWall: blocca le modifiche ai FILE PROTETTI.

Sblocco (STOP gate): crea il file .claude/.unlock-protected e' presente ->
le modifiche passano. Rimuovilo appena finito. I marker vengono azzerati a
ogni inizio sessione (session_start.py).
"""
import json
import os
import sys

PROTECTED = [
    "agent.py",
    "backend/parser/csv_parser.py",
    "prompts/system_prompt_v4.txt",
    "backend/prompts/system_prompt.txt",
    "modules/setup_params.py",
    "app_legacy.py",
]


def norm(p: str) -> str:
    return os.path.normpath(p).replace("\\", "/").lower()


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # input non valido: non bloccare

    ti = data.get("tool_input", {}) or {}
    fp = ti.get("file_path") or ti.get("notebook_path") or ""
    if not fp:
        sys.exit(0)

    target = norm(fp)
    hit = next((p for p in PROTECTED if target.endswith(norm(p))), None)
    if not hit:
        sys.exit(0)

    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    unlock = os.path.join(project, ".claude", ".unlock-protected")
    if os.path.exists(unlock):
        print(f"[guard_protected] STOP gate attivo: modifica a '{hit}' autorizzata.",
              file=sys.stderr)
        sys.exit(0)

    print(
        f"BLOCCATO: '{hit}' e' un FILE PROTETTO di PitWall (fonte di verita' ACC / logica).\n"
        f"Richiede STOP gate + 'ok procedi' esplicito dell'utente.\n"
        f"Per autorizzare: crea il file .claude/.unlock-protected, poi ripeti la modifica\n"
        f"(rimuovilo appena finito).",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
