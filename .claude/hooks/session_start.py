#!/usr/bin/env python3
"""SessionStart hook di PitWall:

1. azzera i marker di sblocco residui (non devono sopravvivere tra sessioni);
2. stampa lo stato git sintetico (regola: 'status a inizio sessione').
Lo stdout viene aggiunto al contesto della sessione.
"""
import os
import subprocess

project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

# 1. cleanup marker di sblocco + stato promemoria (non sopravvivono tra sessioni)
for marker in (".unlock-protected", ".unlock-git", ".reminder-state.json"):
    path = os.path.join(project, ".claude", marker)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def run(args):
    try:
        return subprocess.run(
            args, cwd=project, capture_output=True, text=True, timeout=15
        ).stdout.strip()
    except Exception:
        return ""


branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
head = run(["git", "log", "--oneline", "-1"])
dirty = run(["git", "status", "--short"])

print("=== PitWall - stato di sessione ===")
print(f"branch: {branch or '(n/d)'}")
print(f"HEAD:   {head or '(n/d)'}")
if dirty:
    print("working tree: MODIFICHE PRESENTI:")
    print(dirty)
else:
    print("working tree: PULITO")
print("Guardrail attivi: file protetti, git commit/push, wildcard CSS. "
      "Sblocco via .claude/.unlock-protected | .unlock-git (solo dopo ok utente).")
