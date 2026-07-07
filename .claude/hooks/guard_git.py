#!/usr/bin/env python3
"""PreToolUse guard su Bash: applica la regola 'niente commit/push senza ok push'.

- git commit / git push -> bloccati salvo presenza di .claude/.unlock-git
- git add di file .db -> SEMPRE bloccato (dati auth/utente, gitignored)
Il marker .unlock-git viene azzerato a ogni inizio sessione (session_start.py).
"""
import json
import os
import re
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""
    low = cmd.lower()
    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    if re.search(r"\bgit\s+add\b", low) and ".db" in low:
        print("BLOCCATO: 'git add' su file .db (dati auth/utente, gitignored). "
              "Non tracciare i database.", file=sys.stderr)
        sys.exit(2)

    if re.search(r"\bgit\s+(commit|push)\b", low):
        unlock = os.path.join(project, ".claude", ".unlock-git")
        if os.path.exists(unlock):
            print("[guard_git] Sblocco git attivo: commit/push autorizzato.", file=sys.stderr)
            sys.exit(0)
        print(
            "BLOCCATO: git commit/push richiede 'ok push' esplicito dell'utente.\n"
            "Per autorizzare: crea il file .claude/.unlock-git, poi ripeti il comando\n"
            "(rimuovilo a fine push).",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
