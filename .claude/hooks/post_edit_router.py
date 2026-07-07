#!/usr/bin/env python3
"""PostToolUse router di PitWall.

Dopo una modifica a un file, rileva l'AREA toccata e inietta un promemoria per
far girare l'agente giusto (read-only): codice .py -> verifier, UI/CSS ->
css-ui-guardian, doc d'esame -> doc-sync. Dedup per area entro una finestra
temporale, per non sollecitare a ogni singolo edit di una raffica.
"""
import json
import os
import re
import sys
import time

WINDOW = 600  # secondi: una sola sollecitazione per area in questa finestra


def norm(p: str) -> str:
    return os.path.normpath(p).replace("\\", "/").lower()


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    ti = data.get("tool_input", {}) or {}
    fp = norm(ti.get("file_path") or ti.get("notebook_path") or "")
    if not fp or "/.claude/" in fp:
        sys.exit(0)

    areas = []  # (etichetta, agente)
    if re.search(r"assets/.*\.css$|styles/.*\.css$|(^|/)ui/[^/]+\.py$|assets/.*component", fp):
        areas.append(("UI/CSS", "css-ui-guardian"))
    if fp.endswith(".py"):
        areas.append(("codice Python", "verifier"))
    if re.search(r"(prompt_log|incidents|readme|spec_errata|avvio_rapido)\.md$", fp):
        areas.append(("documentazione d'esame", "doc-sync"))
    if not areas:
        sys.exit(0)

    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    state_path = os.path.join(project, ".claude", ".reminder-state.json")
    try:
        with open(state_path) as fh:
            state = json.load(fh)
    except Exception:
        state = {}

    now = time.time()
    fresh = [(lbl, ag) for (lbl, ag) in areas if now - state.get(ag, 0) > WINDOW]
    if not fresh:
        sys.exit(0)

    for _, ag in fresh:
        state[ag] = now
    try:
        with open(state_path, "w") as fh:
            json.dump(state, fh)
    except Exception:
        pass

    msg = (
        "Area toccata: "
        + "; ".join(f"{lbl} -> agente `{ag}`" for lbl, ag in fresh)
        + ". Prima di dichiarare 'fatto', fai girare l'agente indicato (read-only) e "
        "sintetizzane l'esito. Vedi la cheat-sheet in CLAUDE.md."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
