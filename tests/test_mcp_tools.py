"""Tests for ASME B31.3, HSE L8, BS EN 12056, BS 8558, and CIBSE Guide B tools."""

import pytest
from adlor_mcp_cad.tools.asme_b313 import calculate_min_wall_thickness
from adlor_mcp_cad.tools.hse_l8 import audit_water_loop_compliance
from adlor_mcp_cad.tools.bs_en_12056 import calculate_drainage_pipe_size
from adlor_mcp_cad.tools.bs_8558 import audit_tmv_compliance
from adlor_mcp_cad.tools.cibse_guide_b import calculate_hydronic_pipe_size
from adlor_mcp_cad.batch_audit import audit_piping_schedule


def test_asme_b313_calculation():
    """Verify ASME B31.3 wall thickness and schedule selection."""
    res = calculate_min_wall_thickness(
        design_pressure_bar=20.0,
        design_temp_celsius=180.0,
        pipe_od_mm=168.3,
        corrosion_allowance_mm=3.0,
    )
    assert res.min_required_wall_thickness_mm > 3.0
    assert "Schedule" in res.standard_schedule_recommended
    assert res.status == "COMPLIANT_SPEC"
    assert "ASME B31.3" in res.citation


def test_hse_l8_compliance_check():
    """Verify HSE L8 Legionella compliance auditing."""
    # Compliant scenario
    pass_res = audit_water_loop_compliance(
        calorifier_storage_temp_celsius=62.0,
        flow_temp_celsius=55.0,
        return_temp_celsius=52.0,
        cold_water_temp_celsius=16.0,
    )
    assert pass_res.is_compliant is True
    assert len(pass_res.violations) == 0

    # Non-compliant scenario
    fail_res = audit_water_loop_compliance(
        calorifier_storage_temp_celsius=54.0,  # Below 60C limit
        flow_temp_celsius=48.0,                # Below 50C limit
        return_temp_celsius=45.0,              # Below 50C limit
        cold_water_temp_celsius=22.0,          # Above 20C limit
    )
    assert fail_res.is_compliant is False
    assert len(fail_res.violations) == 4


def test_bs_en_12056_drainage_sizing():
    """Verify BS EN 12056 drainage pipe sizing."""
    res = calculate_drainage_pipe_size(
        appliance_counts={"washbasin": 5, "wc_6_litre": 3, "shower_with_plug": 2},
        building_type="commercial",
    )
    assert res.total_discharge_units > 0
    assert res.design_waste_water_flow_l_s > 0
    assert res.recommended_dn in [32, 40, 50, 75, 100, 150]
    assert "BS EN 12056-2" in res.standard


def test_bs_8558_tmv_compliance():
    """Verify BS 8558 TMV scald prevention compliance."""
    # Compliant washbasin
    pass_tmv = audit_tmv_compliance("washbasin", 40.0)
    assert pass_tmv.is_compliant is True

    # Scald risk at shower
    fail_tmv = audit_tmv_compliance("shower", 46.0)
    assert fail_tmv.is_compliant is False
    assert len(fail_tmv.violations) >= 1
    assert "BS 8558:2015" in fail_tmv.citations[0]


def test_cibse_guide_b_pipe_sizing():
    """Verify CIBSE Guide B hydronic heating pipe sizing."""
    res = calculate_hydronic_pipe_size(
        thermal_load_kw=45.0,
        flow_temp_celsius=80.0,
        return_temp_celsius=60.0,
        max_velocity_m_s=1.2,
    )
    assert res.recommended_dn >= 15
    assert res.fluid_velocity_m_s <= 1.2
    assert res.is_velocity_compliant is True


def test_batch_audit_pipeline():
    """Verify batch audit pipeline on multiple elements."""
    elements = [
        {
            "element_id": "P-101",
            "system_type": "Process Steam",
            "design_pressure_bar": 15.0,
            "design_temp_celsius": 175.0,
            "pipe_od_mm": 114.3,
        },
        {
            "element_id": "W-201",
            "system_type": "Domestic Hot Water",
            "calorifier_temp": 65.0,
            "flow_temp": 58.0,
            "return_temp": 54.0,
            "cold_temp": 14.0,
        },
        {
            "element_id": "H-301",
            "system_type": "LTHW Heating",
            "thermal_load_kw": 30.0,
            "flow_temp": 75.0,
            "return_temp": 55.0,
        },
    ]
    report = audit_piping_schedule(elements)
    assert report.total_elements_audited == 3
    assert report.compliant_elements == 3
    assert report.compliance_rate_percent == 100.0
