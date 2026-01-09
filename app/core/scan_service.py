import asyncio
from datetime import datetime
from app.config import settings
from app.db.repo import ScanRepo
from app.core.robots import is_allowed
from app.core.storage import ensure_dirs
from app.domain.viewports import get_viewports
from app.scanners.playwright_runner import open_and_capture
from app.scanners.axe_runner import run_axe
from app.core.normalize import normalize_axe_results, summarize_findings
from app.reports.pdf import build_pdf

def run_scan_job(scan_id: int):
    scan = ScanRepo.get_scan(scan_id)
    if not scan:
        raise RuntimeError("Scan not found")

    url = scan["url"]

    allowed, robots_info = is_allowed(url)
    if not allowed and settings.allow_robots_deny:
        ScanRepo.set_scan_failed(scan_id, robots_allowed="no", error_message=f"Blocked by robots.txt: {robots_info}")
        return

    dirs = ensure_dirs(scan_id)
    viewports = get_viewports()

    screenshots = {}
    all_findings: list[dict] = []

    # For simplicity we open the page twice per viewport (once for screenshot, once for axe).
    # This keeps logic straightforward and reduces shared-state bugs.
    for vp in viewports:
        vp_name = vp["name"]
        screenshot_path = f"{dirs['screenshots_dir']}/{vp_name}.png"
        screenshots[vp_name] = screenshot_path

        # Screenshot
        asyncio.run(open_and_capture(url, vp, screenshot_path))

        # Axe scan
        raw = asyncio.run(run_axe(url, vp))
        findings = normalize_axe_results(raw, viewport_name=vp_name, screenshot_path=screenshot_path)
        all_findings.extend(findings)

    summary = summarize_findings(all_findings)

    # Persist findings
    ScanRepo.replace_findings(scan_id, all_findings)

    # Build PDF
    report_pdf_path = f"{dirs['reports_dir']}/report.pdf"
    build_pdf(
        out_path=report_pdf_path,
        scan_id=scan_id,
        url=url,
        robots_allowed=allowed,
        summary=summary,
        findings=all_findings,
        screenshots=screenshots,
    )

    ScanRepo.set_scan_done(scan_id, robots_allowed=allowed, summary=summary, report_pdf_path=report_pdf_path)
