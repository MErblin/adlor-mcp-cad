"""BS 8558:2015 Guide to the design, installation, testing and maintenance of services supplying water for domestic use within buildings."""

from typing import List, Optional
from pydantic import BaseModel, Field


# Maximum hot water delivery temperatures (°C) per application from BS 8558:2015 Table 1 / Building Regs Part G
MAX_DELIVERY_TEMPS_CELSIUS = {
    "bidet": 38.0,
    "shower": 41.0,
    "washbasin": 41.0,
    "healthcare_washbasin": 41.0,
    "bath_unassisted": 44.0,
    "bath_assisted": 46.0,
    "kitchen_sink": 50.0,
}


class TMVAuditResult(BaseModel):
    standard: str = "BS 8558:2015 & Building Regs Approved Document G (Section G3)"
    appliance_type: str
    delivered_temp_celsius: float
    max_permitted_temp_celsius: float
    is_compliant: bool
    requires_tmv_type: str  # TMV2 (domestic) or TMV3 (healthcare / NHS D08)
    violations: List[str]
    citations: List[str]


def audit_tmv_compliance(
    appliance_type: str,
    delivered_temp_celsius: float,
    is_healthcare: bool = False,
) -> TMVAuditResult:
    """
    Audits hot water outlet temperature at point of use against BS 8558:2015 Table 1
    and Building Regulations Approved Document G3 (Scald Prevention).
    """
    app_key = appliance_type.lower().replace(" ", "_")
    if is_healthcare and app_key == "washbasin":
        app_key = "healthcare_washbasin"

    max_temp = MAX_DELIVERY_TEMPS_CELSIUS.get(app_key, 43.0)
    violations = []
    citations = []

    required_tmv = "TMV3 (NHS D08 Healthcare Compliant)" if is_healthcare else "TMV2 (BS EN 1111 / BS EN 1287 Domestic)"

    if delivered_temp_celsius > max_temp:
        violations.append(
            f"Delivered water temperature ({delivered_temp_celsius}°C) exceeds the maximum permitted limit of {max_temp}°C for {appliance_type}. Scalding hazard."
        )
        citations.append(
            f"BS 8558:2015 Table 1: Maximum hot water supply temperature for {appliance_type} is {max_temp}°C."
        )
        citations.append(
            "Building Regulations Part G (G3 §3.6): Hot water supplied to baths and basins must be controlled to prevent scalding."
        )

    return TMVAuditResult(
        appliance_type=appliance_type,
        delivered_temp_celsius=delivered_temp_celsius,
        max_permitted_temp_celsius=max_temp,
        is_compliant=len(violations) == 0,
        requires_tmv_type=required_tmv,
        violations=violations,
        citations=citations,
    )
