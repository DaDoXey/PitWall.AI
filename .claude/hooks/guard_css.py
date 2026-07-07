#!/usr/bin/env python3
"""PreToolUse guard: impedisce selettori wildcard '*' in assets/app.css.

Regola PitWall: niente wildcard CSS ne' nuovi selettori interni Streamlit
(criterio 'zero cambiamenti visibili'). Il controllo fine sui selettori
Streamlit resta all'agente css-ui-guardian; qui blocchiamo il caso netto
del selettore universale. Sbloccabile via .claude/.unlock-protected.
"""
import json
import os
import re
import sys


def norm(p: str) -> str:
    return os.path.normpath(p).replace("\\", "/").lower()


def strip_block_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", " ", text, flags=re.S)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    ti = data.get("tool_input", {}) or {}
    if not norm(ti.get("file_path", "")).endswith("assets/app.css"):
        sys.exit(0)

    added = ti.get("new_string") or ti.get("content") or ""
    clean = strip_block_comments(added)
    # selettore universale come selettore vero: '* {', '*,', '> * {', ecc.
    if re.search(r"(^|[\s,>+~(])\*\s*[{,]", clean):
        project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        if os.path.exists(os.path.join(project, ".claude", ".unlock-protected")):
            print("[guard_css] STOP gate attivo: wildcard in app.css autorizzata.",
                  file=sys.stderr)
            sys.exit(0)
        print(
            "BLOCCATO: introdotto un selettore wildcard '*' in assets/app.css.\n"
            "Regola PitWall: niente wildcard ne' nuovi selettori interni Streamlit.\n"
            "Se e' davvero intenzionale, autorizza con .claude/.unlock-protected (STOP gate).",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
