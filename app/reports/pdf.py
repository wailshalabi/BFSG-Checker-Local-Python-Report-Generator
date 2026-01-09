from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os

def build_pdf(
    out_path: str,
    scan_id: int,
    url: str,
    robots_allowed: bool,
    summary: dict,
    findings: list[dict],
    screenshots: dict[str, str],
):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4

    def line(y, text, size=11):
        c.setFont("Helvetica", size)
        c.drawString(20*mm, y*mm, text)

    y = 285
    line(y, f"BFSG Checker Report (Scan #{scan_id})", 16); y -= 10
    line(y, f"URL: {url}", 10); y -= 6
    line(y, f"Generated: {datetime.utcnow().isoformat()}Z", 10); y -= 6
    line(y, f"robots.txt allowed: {'YES' if robots_allowed else 'NO'}", 10); y -= 10

    line(y, "Summary", 13); y -= 8
    line(y, f"Total findings: {summary.get('total', 0)}", 11); y -= 6
    line(y, f"Critical: {summary.get('critical', 0)}  Serious: {summary.get('serious', 0)}  Moderate: {summary.get('moderate', 0)}  Minor: {summary.get('minor', 0)}", 11); y -= 10

    # Screenshots (small)
    line(y, "Screenshots", 13); y -= 6
    img_y = y
    for name, path in screenshots.items():
        if not path or not os.path.exists(path):
            continue
        try:
            img = ImageReader(path)
            c.setFont("Helvetica", 10)
            c.drawString(20*mm, img_y*mm, name.capitalize())
            c.drawImage(img, 20*mm, (img_y-55)*mm, width=80*mm, height=50*mm, preserveAspectRatio=True, mask='auto')
            img_y -= 60
        except Exception:
            pass
    y = img_y - 5

    if y < 90:
        c.showPage()
        y = 285

    line(y, "Top findings (first 20)", 13); y -= 8
    c.setFont("Helvetica", 9)

    for i, f in enumerate(findings[:20], start=1):
        text = f"{i}. [{f.get('impact','').upper()}] {f.get('rule_id')} ({f.get('viewport')})"
        c.drawString(20*mm, y*mm, text); y -= 5

        desc = (f.get('description') or '').strip().replace('\n',' ')
        if desc:
            c.drawString(25*mm, y*mm, f"Desc: {desc[:120]}"); y -= 5

        sel = (f.get('selector') or '').strip()
        if sel:
            c.drawString(25*mm, y*mm, f"Selector: {sel[:120]}"); y -= 5

        hint = (f.get('fix_hint') or '').strip().replace('\n',' ')
        if hint:
            c.drawString(25*mm, y*mm, f"Fix: {hint[:120]}"); y -= 6
        else:
            y -= 2

        if y < 25:
            c.showPage()
            y = 285
            c.setFont("Helvetica", 9)

    c.save()
