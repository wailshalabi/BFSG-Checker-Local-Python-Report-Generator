from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth
from datetime import datetime
import os


# ------------------------------
# Styles for wrapped cells
# ------------------------------
_STYLES = getSampleStyleSheet()

FIX_HINT_STYLE = _STYLES["BodyText"]
FIX_HINT_STYLE.fontName = "Helvetica"
FIX_HINT_STYLE.fontSize = 8
FIX_HINT_STYLE.leading = 10
FIX_HINT_STYLE.spaceBefore = 0
FIX_HINT_STYLE.spaceAfter = 0

SELECTOR_STYLE = _STYLES["BodyText"]
SELECTOR_STYLE.fontName = "Helvetica"
SELECTOR_STYLE.fontSize = 8
SELECTOR_STYLE.leading = 10
SELECTOR_STYLE.spaceBefore = 0
SELECTOR_STYLE.spaceAfter = 0


def _draw_header(c: canvas.Canvas, title: str, subtitle: str | None = None):
    width, height = A4
    c.setFillColor(colors.HexColor("#0B1220"))
    c.rect(0, height - 32 * mm, width, 32 * mm, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(18 * mm, height - 18 * mm, title)

    if subtitle:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#D5E2FF"))
        c.drawString(18 * mm, height - 25 * mm, subtitle)


def _wrap(text: str, max_width_pt: float, font_name: str, font_size: int):
    """Simple word wrap for single-line canvas text areas."""
    if not text:
        return []
    words = str(text).replace("\n", " ").split()
    lines, line = [], ""
    for w in words:
        candidate = (line + " " + w).strip()
        if stringWidth(candidate, font_name, font_size) <= max_width_pt:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def _severity_color(sev: str):
    sev = (sev or "").lower()
    if sev == "critical":
        return colors.HexColor("#B91C1C")  # red
    if sev == "serious":
        return colors.HexColor("#D97706")  # orange
    if sev == "moderate":
        return colors.HexColor("#2563EB")  # blue
    return colors.HexColor("#64748B")      # slate


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

    # ------------------------------
    # Cover / Summary page
    # ------------------------------
    _draw_header(c, "BFSG Checker Report", f"Scan #{scan_id}")

    y = height - 45 * mm
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica", 10)
    c.drawString(18 * mm, y, f"URL: {url}")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"Generated (UTC): {datetime.utcnow().isoformat()}Z")
    y -= 6 * mm
    c.drawString(18 * mm, y, f"robots.txt allowed: {'YES' if robots_allowed else 'NO'}")
    y -= 10 * mm

    # Summary card
    c.setFillColor(colors.HexColor("#F8FAFC"))
    c.roundRect(18 * mm, y - 26 * mm, width - 36 * mm, 28 * mm, 10, stroke=0, fill=1)

    total = int(summary.get("total", 0) or 0)
    crit = int(summary.get("critical", 0) or 0)
    ser = int(summary.get("serious", 0) or 0)
    mod = int(summary.get("moderate", 0) or 0)
    minor = int(summary.get("minor", 0) or 0)

    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(22 * mm, y - 8 * mm, "Summary")

    c.setFont("Helvetica", 10)
    c.drawString(22 * mm, y - 16 * mm, f"Total: {total}")
    c.drawString(52 * mm, y - 16 * mm, f"Critical: {crit}")
    c.drawString(82 * mm, y - 16 * mm, f"Serious: {ser}")
    c.drawString(112 * mm, y - 16 * mm, f"Moderate: {mod}")
    c.drawString(145 * mm, y - 16 * mm, f"Minor: {minor}")

    # Note
    y = y - 35 * mm
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    note = (
        "Automated accessibility pre-check (WCAG-focused). "
        "Automated results cannot fully prove BFSG compliance; manual review is still recommended."
    )
    for ln in _wrap(note, width - 36 * mm, "Helvetica", 9):
        c.drawString(18 * mm, y, ln)
        y -= 5 * mm

    c.showPage()

    # ------------------------------
    # Screenshot pages (BIG)
    # One screenshot per page, large and centered
    # ------------------------------
    for name in ["desktop", "mobile"]:
        path = screenshots.get(name)
        if not path or not os.path.exists(path):
            continue

        _draw_header(c, "Screenshots", f"{name.capitalize()} viewport")
        img = ImageReader(path)

        top = height - 40 * mm
        left = 18 * mm
        right = width - 18 * mm
        bottom = 18 * mm

        avail_w = right - left
        avail_h = top - bottom

        c.drawImage(
            img,
            left,
            bottom,
            width=avail_w,
            height=avail_h,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        c.showPage()

    # ------------------------------
    # Findings table (readable + wrapped Fix hint)
    # ------------------------------
    _draw_header(c, "Findings", "Top issues (first 50 nodes)")
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica", 10)
    c.drawString(18 * mm, height - 42 * mm, "Below are the most actionable findings (limited to 50).")

    rows = [["#", "Severity", "Rule", "Viewport", "Selector", "Fix hint"]]

    for i, f in enumerate(findings[:50], start=1):
        sev = (f.get("impact") or "moderate").lower()
        rule = f.get("rule_id") or ""
        vp = f.get("viewport") or ""

        sel_text = (f.get("selector") or "").replace("\n", "<br/>").strip()
        hint_text = (f.get("fix_hint") or "").replace("\n", "<br/>").strip()

        # Wrap selector and fix hint to avoid table width growth
        sel_para = Paragraph(sel_text if sel_text else "&nbsp;", SELECTOR_STYLE)
        hint_para = Paragraph(hint_text if hint_text else "&nbsp;", FIX_HINT_STYLE)

        rows.append([str(i), sev, rule, vp, sel_para, hint_para])

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B1220")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),

        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),

        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])

    # Color severity column
    for r in range(1, len(rows)):
        sev = rows[r][1]
        style.add("TEXTCOLOR", (1, r), (1, r), _severity_color(sev))
        style.add("FONTNAME", (1, r), (1, r), "Helvetica-Bold")

    col_widths = [
        10 * mm,  # #
        20 * mm,  # Severity
        35 * mm,  # Rule
        18 * mm,  # Viewport
        45 * mm,  # Selector (wrapped)
        62 * mm,  # Fix hint (wrapped)
    ]

    # Manual pagination for the table
    remaining = rows
    first = True
    while remaining:
        if not first:
            _draw_header(c, "Findings", "continued")
        first = False

        max_height = height - 75 * mm
        max_width = width - 36 * mm

        # Find how many rows fit on this page
        fit = min(len(remaining), 35)
        chosen = None
        for n in range(fit, 1, -1):
            t = Table(remaining[:n], colWidths=col_widths, repeatRows=1)
            t.setStyle(style)
            tw, th = t.wrap(max_width, max_height)
            if th <= max_height:
                chosen = t
                fit = n
                break

        if chosen is None:
            # Ensure at least header + one row
            chosen = Table(remaining[:2], colWidths=col_widths, repeatRows=1)
            chosen.setStyle(style)
            fit = 2

        chosen.wrapOn(c, max_width, max_height)
        chosen.drawOn(c, 18 * mm, (height - 60 * mm) - chosen._height)

        remaining = remaining[fit:]
        if remaining:
            c.showPage()

    c.save()
