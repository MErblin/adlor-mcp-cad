"""CIBSE Guide B: Heating and Hydronic Pipe Sizing Calculator (LTHW / Chilled Water)."""

import math
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# Standard carbon steel / copper pipe dimensions (Internal Diameter in mm)
STANDARD_HYDRONIC_PIPES_MM = [
    {"dn": 15, "id_mm": 13.0, "od_mm": 15.0},
    {"dn": 20, "id_mm": 19.0, "od_mm": 22.0},
    {"dn": 25, "id_mm": 25.4, "od_mm": 28.0},
    {"dn": 32, "id_mm": 32.0, "od_mm": 35.0},
    {"dn": 40, "id_mm": 38.1, "od_mm": 42.0},
    {"dn": 50, "id_mm": 50.0, "od_mm": 54.0},
    {"dn": 65, "id_mm": 63.0, "od_mm": 67.0},
    {"dn": 80, "id_mm": 76.0, "od_mm": 80.0},
    {"dn": 100, "id_mm": 100.0, "od_mm": 108.0},
    {"dn": 150, "id_mm": 150.0, "od_mm": 159.0},
]


class HydronicSizingResult(BaseModel):
    standard: str = "CIBSE Guide B (Section B1: Hydronic Heating) / BS EN 12828"
    thermal_load_kw: float
    flow_temp_celsius: float
    return_temp_celsius: float
    delta_t_k: float
    mass_flow_rate_kg_s: float
    volume_flow_rate_l_s: float
    recommended_dn: int
    recommended_id_mm: float
    fluid_velocity_m_s: float
    pressure_drop_pa_per_m: float
    max_velocity_limit_m_s: float
    is_velocity_compliant: bool
    citation: str = "CIBSE Guide B1 §3.4 — Recommended Water Velocities in Buildings"


def calculate_hydronic_pipe_size(
    thermal_load_kw: float,
    flow_temp_celsius: float = 80.0,
    return_temp_celsius: float = 60.0,
    max_pressure_drop_pa_per_m: float = 250.0,
    max_velocity_m_s: float = 1.2,
) -> HydronicSizingResult:
    """
    Calculates required hydronic pipe diameter for Low Temperature Hot Water (LTHW)
    or Chilled Water systems based on thermal load and allowable velocity/pressure drop per CIBSE Guide B.
    
    Formulas:
      - m_dot = Q / (cp * delta_T)   [kg/s]
      - v = (4 * Q_vol) / (pi * d^2) [m/s]
      - dp/L approx = (0.02 * rho * v^2) / (2 * d) (Darcy-Weisbach)
    """
    delta_t = abs(flow_temp_celsius - return_temp_celsius)
    if delta_t == 0:
        delta_t = 20.0  # fallback standard LTHW delta T

    # Specific heat capacity of water approx 4.186 kJ/(kg*K)
    cp = 4.186
    density = 980.0 if flow_temp_celsius >= 60 else 1000.0  # kg/m3

    mass_flow_kg_s = thermal_load_kw / (cp * delta_t)
    volume_flow_m3_s = mass_flow_kg_s / density
    volume_flow_l_s = volume_flow_m3_s * 1000.0

    selected_pipe = STANDARD_HYDRONIC_PIPES_MM[-1]
    computed_velocity = 0.0
    computed_dp = 0.0

    for pipe in STANDARD_HYDRONIC_PIPES_MM:
        d_m = pipe["id_mm"] / 1000.0
        area = (math.pi / 4.0) * (d_m ** 2)
        vel = volume_flow_m3_s / area

        # Estimate Darcy-Weisbach friction factor f approx 0.025 for commercial steel
        friction_factor = 0.025
        dp_per_m = (friction_factor * density * (vel ** 2)) / (2.0 * d_m)

        if vel <= max_velocity_m_s and dp_per_m <= max_pressure_drop_pa_per_m:
            selected_pipe = pipe
            computed_velocity = vel
            computed_dp = dp_per_m
            break
    else:
        # If no pipe under thresholds, pick largest and compute its velocity
        d_m = selected_pipe["id_mm"] / 1000.0
        area = (math.pi / 4.0) * (d_m ** 2)
        computed_velocity = volume_flow_m3_s / area
        computed_dp = (0.025 * density * (computed_velocity ** 2)) / (2.0 * d_m)

    return HydronicSizingResult(
        thermal_load_kw=thermal_load_kw,
        flow_temp_celsius=flow_temp_celsius,
        return_temp_celsius=return_temp_celsius,
        delta_t_k=round(delta_t, 1),
        mass_flow_rate_kg_s=round(mass_flow_kg_s, 3),
        volume_flow_rate_l_s=round(volume_flow_l_s, 3),
        recommended_dn=selected_pipe["dn"],
        recommended_id_mm=selected_pipe["id_mm"],
        fluid_velocity_m_s=round(computed_velocity, 2),
        pressure_drop_pa_per_m=round(computed_dp, 1),
        max_velocity_limit_m_s=max_velocity_m_s,
        is_velocity_compliant=computed_velocity <= max_velocity_m_s,
    )
