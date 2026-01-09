from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.jobs.scheduler import enqueue_scan
from app.db.repo import ScanRepo

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def ui_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/ui/scan")
def ui_create_scan(url: str = Form(...)):
    scan_id = enqueue_scan(url)
    return RedirectResponse(url=f"/ui/scan/{scan_id}", status_code=303)


@router.get("/ui/scan/{scan_id}", response_class=HTMLResponse)
def ui_scan_status(request: Request, scan_id: int):
    scan = ScanRepo.get_scan(scan_id)
    if not scan:
        return templates.TemplateResponse(
            "scan.html",
            {"request": request, "scan_id": scan_id, "scan": None, "error": "Scan not found"},
            status_code=404,
        )
    return templates.TemplateResponse(
        "scan.html",
        {"request": request, "scan_id": scan_id, "scan": scan, "error": None},
    )
