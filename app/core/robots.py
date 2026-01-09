from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests

from app.config import settings

def is_allowed(url: str) -> tuple[bool, str]:
    """Return (allowed, robots_url_or_reason)."""
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        return False, "Invalid URL scheme"

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)

    try:
        # RobotFileParser.read() uses urllib; we use requests for more control
        resp = requests.get(robots_url, timeout=10, headers={"User-Agent": settings.user_agent})
        if resp.status_code >= 400:
            # If robots.txt missing, generally treat as allowed
            rp.parse([])
            return True, robots_url
        rp.parse(resp.text.splitlines())
    except Exception:
        # Network/timeout fetching robots: default allow (common behavior)
        return True, robots_url

    ua = settings.robots_user_agent or "*"
    try:
        return bool(rp.can_fetch(ua, url)), robots_url
    except Exception:
        return True, robots_url
