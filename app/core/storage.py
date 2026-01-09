import os
import json
from pathlib import Path
from app.config import settings

def ensure_dirs(scan_id: int) -> dict:
    base = Path(settings.artifacts_dir)
    screenshots_dir = base / "screenshots" / str(scan_id)
    reports_dir = base / "reports" / str(scan_id)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return {
        "base": str(base),
        "screenshots_dir": str(screenshots_dir),
        "reports_dir": str(reports_dir),
    }

def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
