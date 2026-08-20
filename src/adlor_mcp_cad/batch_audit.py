"""Batch Engineering Audit Pipeline for CAD / BIM piping systems."""

import json
from typing import Dict, List, Any
from pydantic import BaseModel
from adlor_mcp_cad.tools.asme_b313 import calculate_min_wall_thickness
from adlor_mcp_cad.tools.hse_l8 import audit_water_loop_compliance
from adlor_mcp_cad.tools.bs_8558 import audit_tmv_compliance
from adlor_mcp_cad.tools.cibse_guide_b import calculate_hydronic_pipe_size


class ElementAuditSummary(BaseModel):
    element_id: str
    system_type: str
    standard_applied: str
    status: str  # "PASS" | "FAIL" | "WARNING"
    details: Dict[str, Any]


class BatchAuditReport(BaseModel):
    total_elements_audited: int
    compliant_elements: int
    non_compliant_elements: int
    compliance_rate_percent: float
    results: List[ElementAuditSummary]


def audit_piping_schedule(elements: List[Dict[str, Any]]) -> BatchAuditReport:
    """
    Run automated multi-standard engineering compliance audit over a list of BIM/CAD elements.
    """
    results: List[ElementAuditSummary] = []
    pass_count = 0

    for el in elements:
        eid = str(el.get("element_id", f"ELEM-{len(results)+1}"))
        sys_type = el.get("system_type", "Process Piping")

        if "Process" in sys_type or "Steam" in sys_type or "High Pressure" in sys_type:
            res = calculate_min_wall_thickness(
                design_pressure_bar=float(el.get("design_pressure_bar", 10.0)),
                design_temp_celsius=float(el.get("design_temp_celsius", 150.0)),
                pipe_od_mm=float(el.get("pipe_od_mm", 168.3)),
            )
            is_pass = res.status == "COMPLIANT_SPEC"
            if is_pass:
                pass_count += 1
            results.append(
                ElementAuditSummary(
                    element_id=eid,
                    system_type=sys_type,
                    standard_applied=res.standard,
                    status="PASS" if is_pass else "FAIL",
                    details=res.model_dump(),
                )
            )

        elif "Water" in sys_type or "Domestic" in sys_type or "DHW" in sys_type:
            res = audit_water_loop_compliance(
                calorifier_storage_temp_celsius=float(el.get("calorifier_temp", 62.0)),
                flow_temp_celsius=float(el.get("flow_temp", 55.0)),
                return_temp_celsius=float(el.get("return_temp", 52.0)),
                cold_water_temp_celsius=float(el.get("cold_temp", 15.0)),
            )
            if res.is_compliant:
                pass_count += 1
            results.append(
                ElementAuditSummary(
                    element_id=eid,
                    system_type=sys_type,
                    standard_applied=res.standard,
                    status="PASS" if res.is_compliant else "FAIL",
                    details=res.model_dump(),
                )
            )

        elif "Heating" in sys_type or "LTHW" in sys_type:
            res = calculate_hydronic_pipe_size(
                thermal_load_kw=float(el.get("thermal_load_kw", 50.0)),
                flow_temp_celsius=float(el.get("flow_temp", 80.0)),
                return_temp_celsius=float(el.get("return_temp", 60.0)),
            )
            if res.is_velocity_compliant:
                pass_count += 1
            results.append(
                ElementAuditSummary(
                    element_id=eid,
                    system_type=sys_type,
                    standard_applied=res.standard,
                    status="PASS" if res.is_velocity_compliant else "WARNING",
                    details=res.model_dump(),
                )
            )

    total = len(results)
    rate = round((pass_count / total * 100.0), 1) if total > 0 else 100.0

    return BatchAuditReport(
        total_elements_audited=total,
        compliant_elements=pass_count,
        non_compliant_elements=total - pass_count,
        compliance_rate_percent=rate,
        results=results,
    )
