"""UK HSE ACoP L8 Legionella & Thermal Water Loop Compliance Auditor."""

from pydantic import BaseModel, Field
from typing import List, Optional

class WaterLoopAuditResult(BaseModel):
    standard: str = "HSE ACoP L8 (4th Edition) / HSG274 Part 2"
    calorifier_storage_temp_celsius: float
    flow_temp_celsius: float
    return_temp_celsius: float
    cold_water_temp_celsius: float
    is_compliant: bool
    violations: List[str]
    citations: List[str]

def audit_water_loop_compliance(
    calorifier_storage_temp_celsius: float,
    flow_temp_celsius: float,
    return_temp_celsius: float,
    cold_water_temp_celsius: float = 18.0,
) -> WaterLoopAuditResult:
    """
    Audits MEP domestic hot water (DHW) and cold water services against HSE ACoP L8:
    - Calorifier storage: >= 60°C throughout
    - Hot water flow: >= 55°C (healthcare) or >= 50°C (commercial)
    - Hot water return: >= 50°C
    - Cold water storage & distribution: < 20°C
    """
    violations = []
    citations = []

    if calorifier_storage_temp_celsius < 60.0:
        violations.append(
            f"Calorifier storage temp is {calorifier_storage_temp_celsius}°C (Required: >= 60.0°C). Risk of Legionella proliferation."
        )
        citations.append("HSG274 Part 2 §2.10: Calorifiers must store water at minimum 60°C.")

    if flow_temp_celsius < 50.0:
        violations.append(
            f"Distribution flow temperature is {flow_temp_celsius}°C (Required: >= 50.0°C at all outlets)."
        )
        citations.append("HSG274 Part 2 §2.14: Hot water must reach outlets at minimum 50°C within 1 minute.")

    if return_temp_celsius < 50.0:
        violations.append(
            f"Recirculation return temperature is {return_temp_celsius}°C (Required: >= 50.0°C at return to calorifier)."
        )
        citations.append("HSG274 Part 2 §2.16: Return temperatures must not drop below 50°C.")

    if cold_water_temp_celsius >= 20.0:
        violations.append(
            f"Cold water temperature is {cold_water_temp_celsius}°C (Required: < 20.0°C)."
        )
        citations.append("HSG274 Part 2 §2.3: Cold water must remain below 20°C throughout distribution.")

    return WaterLoopAuditResult(
        calorifier_storage_temp_celsius=calorifier_storage_temp_celsius,
        flow_temp_celsius=flow_temp_celsius,
        return_temp_celsius=return_temp_celsius,
        cold_water_temp_celsius=cold_water_temp_celsius,
        is_compliant=len(violations) == 0,
        violations=violations,
        citations=citations,
    )
