"""BS EN 12056-2:2000 Gravity Drainage Systems Inside Buildings — Pipe Sizing Calculator."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# Standard Discharge Units (DU) per appliance from BS EN 12056-2 Table 2 (System I)
STANDARD_APPLIANCE_DU = {
    "washbasin": 0.5,
    "bidet": 0.5,
    "shower_without_plug": 0.6,
    "shower_with_plug": 0.8,
    "single_bath": 0.8,
    "wc_6_litre": 2.0,
    "wc_7_5_litre": 2.0,
    "wc_9_litre": 2.5,
    "kitchen_sink": 0.8,
    "dishwasher_domestic": 0.8,
    "washing_machine_domestic": 0.8,
    "urinal_single": 0.5,
    "commercial_sink": 1.5,
    "commercial_dishwasher": 2.5,
}

# Discharge capacity Q_max (L/s) for standard pipe sizes at 1:50 gradient (BS EN 12056-2 Table 6)
DRAINAGE_PIPE_CAPACITIES_L_PER_S = [
    {"dn": 32, "od_mm": 36.0, "max_flow_l_s": 0.5, "min_gradient": "1:50"},
    {"dn": 40, "od_mm": 43.0, "max_flow_l_s": 0.8, "min_gradient": "1:50"},
    {"dn": 50, "od_mm": 56.0, "max_flow_l_s": 1.5, "min_gradient": "1:50"},
    {"dn": 75, "od_mm": 82.0, "max_flow_l_s": 2.8, "min_gradient": "1:50"},
    {"dn": 100, "od_mm": 110.0, "max_flow_l_s": 5.9, "min_gradient": "1:50"},
    {"dn": 150, "od_mm": 160.0, "max_flow_l_s": 18.0, "min_gradient": "1:50"},
]


class DrainageSizingResult(BaseModel):
    standard: str = "BS EN 12056-2:2000 (System I)"
    total_discharge_units: float
    frequency_factor_k: float
    design_waste_water_flow_l_s: float
    recommended_dn: int
    recommended_od_mm: float
    max_flow_capacity_l_s: float
    capacity_utilisation_percent: float
    citation: str = "BS EN 12056-2:2000 §6.3.2 & Table 6"


def calculate_drainage_pipe_size(
    appliance_counts: Dict[str, int],
    building_type: str = "commercial",
    frequency_factor_k: Optional[float] = None,
) -> DrainageSizingResult:
    """
    Calculate required internal drainage pipe diameter according to BS EN 12056-2:2000.
    
    Formula: Qww = K * sqrt(sum(DU))
    where:
      - Qww = waste water flow rate (L/s)
      - K = frequency factor (0.5 for residential, 0.7 for commercial/office, 1.0 for public/hospital)
      - DU = total discharge units
    """
    if frequency_factor_k is None:
        k_factors = {
            "residential": 0.5,
            "dwelling": 0.5,
            "office": 0.7,
            "commercial": 0.7,
            "hotel": 0.7,
            "hospital": 1.0,
            "school": 1.0,
            "public": 1.2,
        }
        k = k_factors.get(building_type.lower(), 0.7)
    else:
        k = frequency_factor_k

    total_du = 0.0
    for appliance, count in appliance_counts.items():
        unit_du = STANDARD_APPLIANCE_DU.get(appliance.lower(), 0.8)
        total_du += unit_du * count

    # Design waste water flow rate Qww = K * sqrt(sum(DU))
    q_ww = round(k * (total_du ** 0.5), 2)

    # Select minimum pipe diameter where capacity >= q_ww
    selected_pipe = DRAINAGE_PIPE_CAPACITIES_L_PER_S[-1]
    for pipe in DRAINAGE_PIPE_CAPACITIES_L_PER_S:
        if pipe["max_flow_l_s"] >= q_ww:
            selected_pipe = pipe
            break

    utilisation = round((q_ww / selected_pipe["max_flow_l_s"]) * 100.0, 1)

    return DrainageSizingResult(
        total_discharge_units=round(total_du, 2),
        frequency_factor_k=k,
        design_waste_water_flow_l_s=q_ww,
        recommended_dn=selected_pipe["dn"],
        recommended_od_mm=selected_pipe["od_mm"],
        max_flow_capacity_l_s=selected_pipe["max_flow_l_s"],
        capacity_utilisation_percent=utilisation,
    )
