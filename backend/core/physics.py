from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ACCPhysicsConstants:
    SAFE_PRESSURE_COLD_MIN: float = 26.0
    SAFE_PRESSURE_COLD_MAX: float = 27.0
    TARGET_PRESSURE_COLD: float = 26.7
    HOT_PRESSURE_DELTA_MIN: float = 2.5
    HOT_PRESSURE_DELTA_MAX: float = 3.5
    TEMP_COMPENSATION_PER_C: float = 0.1
    OPERATING_TEMP_MIN: float = 75.0
    OPERATING_TEMP_MAX: float = 95.0
    HOT_PRESSURE_MIN: float = 28.5
    HOT_PRESSURE_MAX: float = 30.0
    HOT_PRESSURE_TARGET: float = 29.0


class ACCPhysicsEngine:
    """Calcoli deterministici per Assetto Corsa Competizione 1.9+."""

    CONSTANTS = ACCPhysicsConstants()

    @classmethod
    def validate_cold_pressure(cls, pressure_psi: float) -> bool:
        return cls.CONSTANTS.SAFE_PRESSURE_COLD_MIN <= pressure_psi <= cls.CONSTANTS.SAFE_PRESSURE_COLD_MAX

    @classmethod
    def cold_to_hot_pressure(cls, pressure_cold_psi: float, ambient_delta_c: float = 0.0) -> float:
        """Stima la pressione a caldo partendo dalla pressione a freddo in garage."""
        hot_delta = cls.CONSTANTS.TEMP_COMPENSATION_PER_C * ambient_delta_c
        base_hot = pressure_cold_psi + cls.CONSTANTS.HOT_PRESSURE_DELTA_MIN
        return round(base_hot + hot_delta, 2)

    @classmethod
    def adjust_pressure_for_temperature(cls, pressure_cold_psi: float, temperature_celsius: float) -> float:
        """Stima la pressione a caldo usando una compensazione termica esplicita."""
        temp_delta = max(0.0, temperature_celsius - cls.CONSTANTS.OPERATING_TEMP_MIN)
        return round(pressure_cold_psi + cls.CONSTANTS.HOT_PRESSURE_DELTA_MIN + temp_delta * cls.CONSTANTS.TEMP_COMPENSATION_PER_C, 2)

    @classmethod
    def validate_operating_temperature(cls, temperature_celsius: float) -> bool:
        return cls.CONSTANTS.OPERATING_TEMP_MIN <= temperature_celsius <= cls.CONSTANTS.OPERATING_TEMP_MAX

    @classmethod
    def classify_pressure_context(cls, psi: float, context: str) -> Dict[str, any]:
        """
        Classifica una pressione in base al contesto di misurazione.

        Args:
            psi: Valore di pressione in PSI.
            context: 'cold' per pressioni impostate in garage,
                     'hot' per pressioni lette dal MFD in pista.

        Returns:
            Dict con target, delta, in_range e status della pressione.

        Raises:
            ValueError: Se context non è 'cold' o 'hot'.
        """
        if context == "cold":
            target = cls.CONSTANTS.TARGET_PRESSURE_COLD
            min_val = cls.CONSTANTS.SAFE_PRESSURE_COLD_MIN
            max_val = cls.CONSTANTS.SAFE_PRESSURE_COLD_MAX
        elif context == "hot":
            target = cls.CONSTANTS.HOT_PRESSURE_TARGET
            min_val = cls.CONSTANTS.HOT_PRESSURE_MIN
            max_val = cls.CONSTANTS.HOT_PRESSURE_MAX
        else:
            raise ValueError("context deve essere 'cold' oppure 'hot'")

        delta = round(psi - target, 2)
        in_range = min_val <= psi <= max_val

        if abs(delta) <= 0.3:
            status = "optimal"
        elif abs(delta) <= 0.7:
            status = "warning"
        elif delta > 0.7:
            status = "hot"
        else:
            status = "cold"

        return {
            "psi": psi,
            "context": context,
            "target": target,
            "delta": delta,
            "in_range": in_range,
            "status": status,
        }

    @classmethod
    def validate_pressure_context(cls, pressure_psi: float, context: str) -> bool:
        """Valida una pressione in base al contesto di misurazione."""
        classification = cls.classify_pressure_context(pressure_psi, context)
        return classification["in_range"]


def calculate_fuel_load(
    race_duration_min: float,
    lap_time_min: float,
    fuel_cons_per_lap: float,
    safety_margin: float = 0.05,
) -> Dict[str, float]:
    if race_duration_min <= 0:
        raise ValueError("La durata della gara deve essere maggiore di 0.")
    if lap_time_min <= 0:
        raise ValueError("Il tempo del giro deve essere maggiore di 0.")
    if fuel_cons_per_lap <= 0:
        raise ValueError("Il consumo per giro deve essere maggiore di 0.")
    if safety_margin < 0:
        raise ValueError("Il margine di sicurezza non può essere negativo.")

    laps_needed = int((race_duration_min / lap_time_min) + 0.9999)
    fuel_needed = round(laps_needed * fuel_cons_per_lap, 2)
    fuel_recommended = round(fuel_needed * (1 + safety_margin), 2)

    return {
        "laps_needed": laps_needed,
        "fuel_needed_L": fuel_needed,
        "fuel_recommended_L": fuel_recommended,
        "safety_margin_pct": round(safety_margin * 100, 2),
    }


def validate_pressure(pressure_psi: float) -> bool:
    """Valida una pressione a freddo secondo le regole ACC del motore fisico."""
    return ACCPhysicsEngine.validate_cold_pressure(pressure_psi)


def validate_temperature(temperature_celsius: float) -> bool:
    """Valida una temperatura operativa gomme secondo la logica fisica ACC."""
    return ACCPhysicsEngine.validate_operating_temperature(temperature_celsius)
