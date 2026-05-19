import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend.core.physics import ACCPhysicsEngine, calculate_fuel_load

PASS = "✅ PASS"
FAIL = "❌ FAIL"


def test(name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    line = f"{status}  {name}"
    if detail:
        line += f"\n        → {detail}"
    print(line)


print("\n── TC-01: Verifica pressioni ACC ────────────────────────────")

p = 26.7
print("Valid cold pressure:", ACCPhysicsEngine.validate_cold_pressure(p))
test(
    "TC-01a: pressione fredda nel range sicuro",
    ACCPhysicsEngine.validate_cold_pressure(p),
    f"{p} PSI dovrebbe essere valido"
)

test(
    "TC-01b: pressione fredda sotto il range",
    not ACCPhysicsEngine.validate_cold_pressure(25.5),
)

print("\n── TC-02: Calcolo pressione a caldo ─────────────────────────")

hot = ACCPhysicsEngine.cold_to_hot_pressure(26.7, ambient_delta_c=5)
print(f"Pressione stimata a caldo: {hot} PSI")
test(
    "TC-02a: hot pressure calcolata",
    hot >= 29.2,
    f"Atteso almeno 29.2, ottenuto {hot}"
)

print("\n── TC-03: Calcolo carburante ───────────────────────────────")
result = calculate_fuel_load(race_duration_min=20, lap_time_min=1.8667, fuel_cons_per_lap=3.2)
expected_laps = math.ceil(20 / 1.8667)
expected_fuel = round(expected_laps * 3.2, 2)
expected_total = round(expected_fuel * 1.05, 2)

test(
    "TC-03a: laps_needed corretto",
    result["laps_needed"] == expected_laps,
    f"Ottenuto {result['laps_needed']}, atteso {expected_laps}"
)
test(
    "TC-03b: fuel_needed corretto",
    result["fuel_needed_L"] == expected_fuel,
    f"Ottenuto {result['fuel_needed_L']}, atteso {expected_fuel}"
)
test(
    "TC-03c: fuel_recommended corretto",
    abs(result["fuel_recommended_L"] - expected_total) <= 0.5,
    f"Ottenuto {result['fuel_recommended_L']}, atteso circa {expected_total}"
)

print("\n── TC-04: Validazione input errati ─────────────────────────")

try:
    calculate_fuel_load(0, 1.5, 3.2)
    test("TC-04a: durata gara zero", False, "Doveva sollevare ValueError")
except ValueError:
    test("TC-04a: durata gara zero", True)

try:
    calculate_fuel_load(10, 0, 3.2)
    test("TC-04b: tempo giro zero", False, "Doveva sollevare ValueError")
except ValueError:
    test("TC-04b: tempo giro zero", True)
