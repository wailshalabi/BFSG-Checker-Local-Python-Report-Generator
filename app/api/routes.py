from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from app.db.repo import ScanRepo
from app.jobs.scheduler import enqueue_scan

router = APIRouter()

class ScanRequest(BaseModel):
    url: HttpUrl

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/scan")
def create_scan(req: ScanRequest):
    scan_id = enqueue_scan(str(req.url))
    return {"scan_id": scan_id, "status": "queued"}

@router.get("/scan/{scan_id}")
def get_scan(scan_id: int):
    scan = ScanRepo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scans")
def list_scans(limit: int = 50):
    return {"items": ScanRepo.list_scans(limit=limit)}

@router.get("/report/{scan_id}.pdf")
def get_report(scan_id: int):
    scan = ScanRepo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    path = scan.get("report_pdf_path")
    if not path:
        raise HTTPException(status_code=404, detail="Report not available")
    return FileResponse(path, media_type="application/pdf", filename=f"bfsg_report_{scan_id}.pdf")
