import json
from datetime import datetime
from sqlalchemy import select, update
from app.db.session import get_session
from app.db.models import Scan, Finding

class ScanRepo:
    @staticmethod
    def create_scan(url: str) -> int:
        with get_session() as db:
            scan = Scan(url=url, status="queued", robots_allowed="unknown")
            db.add(scan)
            db.commit()
            db.refresh(scan)
            return scan.id

    @staticmethod
    def claim_next_queued_scan() -> int | None:
        """Claim one queued scan (SQLite-safe via optimistic update)."""
        with get_session() as db:
            scan_id = db.scalar(select(Scan.id).where(Scan.status == "queued").order_by(Scan.id.asc()))
            if scan_id is None:
                return None
            res = db.execute(
                update(Scan)
                .where(Scan.id == scan_id, Scan.status == "queued")
                .values(status="running", started_at=datetime.utcnow(), error_message=None)
            )
            db.commit()
            if res.rowcount == 1:
                return scan_id
            return None

    @staticmethod
    def set_scan_done(scan_id: int, robots_allowed: bool, summary: dict, report_pdf_path: str):
        with get_session() as db:
            scan = db.get(Scan, scan_id)
            if not scan:
                return
            scan.status = "done"
            scan.robots_allowed = "yes" if robots_allowed else "no"
            scan.summary_json = json.dumps(summary, ensure_ascii=False)
            scan.report_pdf_path = report_pdf_path
            scan.finished_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def set_scan_failed(scan_id: int, robots_allowed: str = "unknown", error_message: str = "Scan failed"):
        with get_session() as db:
            scan = db.get(Scan, scan_id)
            if not scan:
                return
            scan.status = "failed"
            scan.robots_allowed = robots_allowed
            scan.error_message = error_message
            scan.finished_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def replace_findings(scan_id: int, findings: list[dict]):
        with get_session() as db:
            scan = db.get(Scan, scan_id)
            if not scan:
                return

            # delete existing
            db.query(Finding).filter(Finding.scan_id == scan_id).delete()
            db.commit()

            for f in findings:
                db.add(Finding(
                    scan_id=scan_id,
                    viewport=f.get("viewport", "unknown"),
                    rule_id=f.get("rule_id", ""),
                    impact=f.get("impact"),
                    wcag=json.dumps(f.get("wcag", []), ensure_ascii=False),
                    description=f.get("description"),
                    help_url=f.get("help_url"),
                    selector=f.get("selector"),
                    html=f.get("html"),
                    screenshot_path=f.get("screenshot_path"),
                    fix_hint=f.get("fix_hint"),
                    code_snippet=f.get("code_snippet"),
                ))
            db.commit()

    @staticmethod
    def get_scan(scan_id: int) -> dict | None:
        with get_session() as db:
            scan = db.get(Scan, scan_id)
            if not scan:
                return None
            findings = db.scalars(select(Finding).where(Finding.scan_id == scan_id).order_by(Finding.id.asc())).all()
            summary = json.loads(scan.summary_json) if scan.summary_json else None
            return {
                "id": scan.id,
                "url": scan.url,
                "status": scan.status,
                "robots_allowed": scan.robots_allowed,
                "error_message": scan.error_message,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
                "summary": summary,
                "report_pdf_path": scan.report_pdf_path,
                "report_pdf_url": f"/report/{scan.id}.pdf" if scan.report_pdf_path else None,
                "findings": [
                    {
                        "id": f.id,
                        "viewport": f.viewport,
                        "rule_id": f.rule_id,
                        "impact": f.impact,
                        "wcag": json.loads(f.wcag) if f.wcag else [],
                        "description": f.description,
                        "help_url": f.help_url,
                        "selector": f.selector,
                        "html": f.html,
                        "screenshot_path": f.screenshot_path,
                        "fix_hint": f.fix_hint,
                        "code_snippet": f.code_snippet,
                    } for f in findings
                ]
            }

    @staticmethod
    def list_scans(limit: int = 50) -> list[dict]:
        with get_session() as db:
            scans = db.scalars(select(Scan).order_by(Scan.id.desc()).limit(limit)).all()
            items = []
            for s in scans:
                items.append({
                    "id": s.id,
                    "url": s.url,
                    "status": s.status,
                    "robots_allowed": s.robots_allowed,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "finished_at": s.finished_at.isoformat() if s.finished_at else None,
                    "report_pdf_url": f"/report/{s.id}.pdf" if s.report_pdf_path else None,
                })
            return items
