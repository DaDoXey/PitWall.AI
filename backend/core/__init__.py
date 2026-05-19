"""Modulo core di PitWall.AI: fisica e AI wrapper."""

from .ai_logic import ClaudeEngine
from .physics import (
    ACCPhysicsEngine,
    calculate_fuel_load,
    validate_pressure,
    validate_temperature,
)

__all__ = [
    "ClaudeEngine",
    "ACCPhysicsEngine",
    "calculate_fuel_load",
    "validate_pressure",
    "validate_temperature",
]
