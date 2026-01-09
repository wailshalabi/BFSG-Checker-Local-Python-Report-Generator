def impact_to_severity(impact: str | None) -> str:
    # axe impacts: minor, moderate, serious, critical
    if not impact:
        return "moderate"
    impact = impact.lower()
    if impact in {"critical", "serious", "moderate", "minor"}:
        return impact
    return "moderate"
