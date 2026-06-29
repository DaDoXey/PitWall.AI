"""ui/demo_data.py — SORGENTE DATI DEMO UNICA (Monza · BMW M4 GT3).

Tutti i numeri della demo "blindata" (Dashboard, Telemetria, Heatmap) leggono
DA QUI: un'unica fonte garantisce coerenza tra le schermate (requisito della
checklist pre-demo). Dati HARDCODED e coerenti con la storia:

    A Monza la BMW M4 GT3 surriscalda la posteriore destra (Post.DX) a causa
    delle pressioni basse al retrotreno.

DISTINZIONE PRESSIONI (obbligatoria, vedi SPEC_ERRATA.md):
  - COLD_PRESSURES  → pressioni a FREDDO, come da CSV/garage.
  - HOT_PRESSURES   → pressioni a CALDO, come mostrate sul display telemetria.
Le due NON sono equivalenti e non vanno mai mescolate.
"""

# ─────────────────────────────────────────────
# SESSIONE
# ─────────────────────────────────────────────
SESSION = {
    "track": "Monza",
    "track_nick": "Tempio della Velocità",
    "car": "BMW M4 GT3",
    "car_year": "2024",
    "laps": 8,
    "best_lap": "1:47.812",
    "stint": "Asciutto",
    "fuel_avg_per_lap": 3.2,   # L/giro
    "fuel_total": 25.6,        # L (= 8 × 3.2)
}

# Etichette gomme coerenti con la legenda telemetria.
TYRE_LABELS = {
    "fl": "Ant.SX",
    "fr": "Ant.DX",
    "rl": "Post.SX",
    "rr": "Post.DX",
}

# ─────────────────────────────────────────────
# TEMPERATURE GOMME — 8 giri (°C)
# Serie crescenti; la Post.DX (rr) sfora il limite finestra e arriva a 105°C.
# Il MAX di ogni serie (= ultimo valore) alimenta la heatmap: 88 / 90 / 95 / 105.
# ─────────────────────────────────────────────
TYRE_TEMP_SERIES = {
    "fl": [78, 80, 82, 83, 85, 86, 87, 88],
    "fr": [79, 81, 83, 85, 86, 88, 89, 90],
    "rl": [80, 83, 86, 88, 90, 92, 93, 95],
    "rr": [82, 86, 90, 94, 98, 101, 103, 105],
}

# Limite "finestra" temperatura (linea tratteggiata nel line chart).
TEMP_LIMIT = 95          # °C
TEMP_SCALE = (80, 105)   # scala colore heatmap (blu → rosso)

# Massimi per gomma (= valore heatmap). Derivati dalle serie per non divergere.
TYRE_TEMP_MAX = {pos: max(vals) for pos, vals in TYRE_TEMP_SERIES.items()}
# → {"fl": 88, "fr": 90, "rl": 95, "rr": 105}

# ─────────────────────────────────────────────
# PRESSIONI (psi)
# ─────────────────────────────────────────────
# A CALDO — display telemetria. Finestra ottimale 27.0–27.8 psi.
HOT_PRESSURES = {"fl": 27.4, "fr": 27.5, "rl": 26.2, "rr": 26.0}
HOT_PRESS_WINDOW = (27.0, 27.8)   # psi

# A FREDDO — riferimento CSV/garage (NON usato nei gauge "a caldo").
COLD_PRESSURES = {"fl": 26.5, "fr": 26.5, "rl": 26.2, "rr": 26.0}

# Pressione media (a caldo) per la card Dashboard.
# Coerente con i 4 gauge: media aritmetica dei 4 valori HOT.
PRESS_AVG_HOT = round(sum(HOT_PRESSURES.values()) / 4, 1)   # → 26.8

# ─────────────────────────────────────────────
# CARBURANTE — consumo per giro (L), "stabile" attorno a 3.2
# ─────────────────────────────────────────────
FUEL_PER_LAP = [3.2, 3.1, 3.3, 3.0, 3.2, 3.3, 3.2, 3.3]


def lap_axis():
    """Asse giri 1..N coerente con la lunghezza delle serie."""
    return list(range(1, SESSION["laps"] + 1))
