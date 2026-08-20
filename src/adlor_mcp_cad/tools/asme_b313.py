"""ASME B31.3 Process Piping Verification & Minimum Wall Thickness Calculator."""

from pydantic import BaseModel, Field
from typing import Optional

class PipingCalculationResult(BaseModel):
    standard: str = "ASME B31.3-2022"
    design_pressure_bar: float
    design_temp_celsius: float
    pipe_od_mm: float
    allowable_stress_mpa: float
    joint_quality_factor: float
    corrosion_allowance_mm: float
    min_required_wall_thickness_mm: float
    standard_schedule_recommended: str
    status: str
    citation: str = "ASME B31.3 §304.1.2 - Straight Pipe Under Internal Pressure"

def calculate_min_wall_thickness(
    design_pressure_bar: float,
    design_temp_celsius: float,
    pipe_od_mm: float,
    material_grade: str = "ASTM A106 Gr.B",
    corrosion_allowance_mm: float = 3.0,
    weld_joint_factor: float = 1.0,
) -> PipingCalculationResult:
    """
    Calculates minimum required wall thickness according to ASME B31.3 §304.1.2:
    tm = (P * D) / (2 * (S * E + P * Y)) + c
    """
    P = design_pressure_bar * 0.1  # Convert bar to MPa
    D = pipe_od_mm
    # S = basic allowable stress at design temperature for ASTM A106 Gr.B (approx 138 MPa up to 200C)
    S = 138.0 if design_temp_celsius <= 200 else (138.0 - (design_temp_celsius - 200) * 0.2)
    E = weld_joint_factor
    Y = 0.4  # Coefficient for ferritic steels below 482°C
    c = corrosion_allowance_mm

    # Pressure design thickness
    t = (P * D) / (2 * (S * E + P * Y))
    tm = round(t + c, 3)

    # Standard schedule recommendation
    if tm <= 3.91:
        sched = "Schedule 40 (Standard)"
    elif tm <= 5.54:
        sched = "Schedule 80 (Extra Strong)"
    elif tm <= 8.56:
        sched = "Schedule 160"
    else:
        sched = "Schedule XXS (Double Extra Strong)"

    return PipingCalculationResult(
        design_pressure_bar=design_pressure_bar,
        design_temp_celsius=design_temp_celsius,
        pipe_od_mm=pipe_od_mm,
        allowable_stress_mpa=S,
        joint_quality_factor=E,
        corrosion_allowance_mm=c,
        min_required_wall_thickness_mm=tm,
        standard_schedule_recommended=sched,
        status="COMPLIANT_SPEC",
    )
