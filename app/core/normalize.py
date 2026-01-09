from app.domain.severity import impact_to_severity
from app.domain.hints import enrich

def normalize_axe_results(raw: dict, viewport_name: str, screenshot_path: str | None = None) -> list[dict]:
    findings: list[dict] = []
    violations = raw.get("violations", []) if isinstance(raw, dict) else []
    for v in violations:
        rule_id = v.get("id", "unknown")
        impact = v.get("impact")
        desc = v.get("description") or v.get("help")
        help_url = v.get("helpUrl")

        hint = enrich(rule_id)

        nodes = v.get("nodes", []) or []
        # Create one finding per node (more actionable); cap to avoid huge output
        for node in nodes[:30]:
            selector = None
            targets = node.get("target")
            if isinstance(targets, list) and targets:
                selector = " ".join(str(t) for t in targets[:2])
            html = node.get("html")
            findings.append({
                "viewport": viewport_name,
                "rule_id": rule_id,
                "impact": impact_to_severity(impact),
                "description": desc,
                "help_url": help_url,
                "selector": selector,
                "html": html,
                "screenshot_path": screenshot_path,
                "wcag": hint.get("wcag", []),
                "fix_hint": hint.get("fix_hint"),
                "code_snippet": hint.get("code_snippet"),
            })
    return findings

def summarize_findings(findings: list[dict]) -> dict:
    counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for f in findings:
        sev = (f.get("impact") or "moderate").lower()
        if sev not in counts:
            sev = "moderate"
        counts[sev] += 1
    total = sum(counts.values())
    return {"total": total, **counts}
