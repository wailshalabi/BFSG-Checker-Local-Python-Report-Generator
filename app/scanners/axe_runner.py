import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from app.config import settings

AXE_RUN_JS = """async () => {
  const options = {
    runOnly: { type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa','best-practice'] }
  };
  const results = await axe.run(document, options);
  return results;
}
"""


def _load_axe_source() -> str:
    p = Path(settings.axe_path)
    if not p.exists():
        raise FileNotFoundError(
            f"axe.min.js not found at {p}. If running locally, add it under ./vendor/axe/axe.min.js. "
            "Docker build vendors it automatically."
        )
    return p.read_text(encoding="utf-8")

async def run_axe(url: str, viewport: dict) -> dict:
    axe_src = _load_axe_source()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]},
            user_agent=settings.user_agent,
        )
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=settings.max_navigation_wait_ms)
        try:
            await page.wait_for_load_state("networkidle", timeout=min(settings.scan_timeout_ms, 15000))
        except Exception:
            pass

        await page.add_script_tag(content=axe_src)
        results = await page.evaluate(AXE_RUN_JS)

        await context.close()
        await browser.close()
        return results
