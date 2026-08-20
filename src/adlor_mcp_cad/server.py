"""FastMCP Server for Autodesk Revit, IFC & UK/International Engineering Standards Compliance."""

import json
from typing import Dict, Optional
from mcp.server.fastmcp import FastMCP
from adlor_mcp_cad.tools.asme_b313 import calculate_min_wall_thickness
from adlor_mcp_cad.tools.hse_l8 import audit_water_loop_compliance
from adlor_mcp_cad.tools.bs_en_12056 import calculate_drainage_pipe_size
from adlor_mcp_cad.tools.bs_8558 import audit_tmv_compliance
from adlor_mcp_cad.tools.cibse_guide_b import calculate_hydronic_pipe_size

mcp = FastMCP("adlor-mcp-cad")


@mcp.tool()
def check_piping_clearance_asme_b313(
    design_pressure_bar: float,
    design_temp_celsius: float,
    pipe_od_mm: float,
    corrosion_allowance_mm: float = 3.0,
) -> str:
    """Calculate minimum required pipe wall thickness and recommended schedule under ASME B31.3-2022 Process Piping Standard (§304.1.2)."""
    res = calculate_min_wall_thickness(
        design_pressure_bar=design_pressure_bar,
        design_temp_celsius=design_temp_celsius,
        pipe_od_mm=pipe_od_mm,
        corrosion_allowance_mm=corrosion_allowance_mm,
    )
    return json.dumps(res.model_dump(), indent=2)


@mcp.tool()
def audit_mep_water_loop_hse_l8(
    calorifier_storage_temp_celsius: float,
    flow_temp_celsius: float,
    return_temp_celsius: float,
    cold_water_temp_celsius: float = 18.0,
) -> str:
    """Audit MEP domestic hot and cold water system temperatures against UK HSE ACoP L8 and HSG274 Part 2 Legionella control requirements."""
    res = audit_water_loop_compliance(
        calorifier_storage_temp_celsius=calorifier_storage_temp_celsius,
        flow_temp_celsius=flow_temp_celsius,
        return_temp_celsius=return_temp_celsius,
        cold_water_temp_celsius=cold_water_temp_celsius,
    )
    return json.dumps(res.model_dump(), indent=2)


@mcp.tool()
def size_drainage_pipe_bs_en_12056(
    washbasins: int = 0,
    wcs: int = 0,
    showers: int = 0,
    sinks: int = 0,
    building_type: str = "commercial",
) -> str:
    """Calculate required internal gravity drainage pipe diameter under BS EN 12056-2:2000 (System I) based on fixture discharge units (DU)."""
    counts = {
        "washbasin": washbasins,
        "wc_6_litre": wcs,
        "shower_with_plug": showers,
        "commercial_sink": sinks,
    }
    res = calculate_drainage_pipe_size(counts, building_type=building_type)
    return json.dumps(res.model_dump(), indent=2)


@mcp.tool()
def audit_tmv_compliance_bs_8558(
    appliance_type: str,
    delivered_temp_celsius: float,
    is_healthcare: bool = False,
) -> str:
    """Audit hot water outlet temperature against BS 8558:2015 Table 1 and Building Regulations Part G (G3 Scald Prevention)."""
    res = audit_tmv_compliance(
        appliance_type=appliance_type,
        delivered_temp_celsius=delivered_temp_celsius,
        is_healthcare=is_healthcare,
    )
    return json.dumps(res.model_dump(), indent=2)


@mcp.tool()
def calculate_hydronic_pipe_cibse_b(
    thermal_load_kw: float,
    flow_temp_celsius: float = 80.0,
    return_temp_celsius: float = 60.0,
    max_velocity_m_s: float = 1.2,
) -> str:
    """Calculate required LTHW / Chilled Water pipe diameter and pressure drop under CIBSE Guide B Section B1 and BS EN 12828."""
    res = calculate_hydronic_pipe_size(
        thermal_load_kw=thermal_load_kw,
        flow_temp_celsius=flow_temp_celsius,
        return_temp_celsius=return_temp_celsius,
        max_velocity_m_s=max_velocity_m_s,
    )
    return json.dumps(res.model_dump(), indent=2)


@mcp.tool()
def query_bim_element_properties(element_id: str, category: str = "Piping") -> str:
    """Query simulated 3D BIM model element geometry, insulation, and system attributes."""
    sample_element = {
        "element_id": element_id,
        "category": category,
        "family": "Carbon Steel Sch 40 Butt-Weld",
        "nominal_diameter_mm": 150.0,
        "outer_diameter_mm": 168.3,
        "insulation_type": "Mineral Wool Class 0",
        "insulation_thickness_mm": 50.0,
        "system_classification": "High Pressure Process Steam",
        "spatial_clearance_to_nearest_beam_mm": 65.0,
        "min_required_clearance_mm": 50.0,
        "clash_detected": False,
    }
    return json.dumps(sample_element, indent=2)


def run_server():
    mcp.run()


if __name__ == "__main__":
    run_server()
