import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from app.config import settings

async def open_and_capture(url: str, viewport: dict, screenshot_path: str) -> dict:
    """Open URL with given viewport and return minimal page info."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]},
            user_agent=settings.user_agent,
        )
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=settings.max_navigation_wait_ms)
        # Give SPAs a moment to settle; keep it short for single page MVP
        try:
            await page.wait_for_load_state("networkidle", timeout=min(settings.scan_timeout_ms, 15000))
        except Exception:
            pass

        Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=screenshot_path, full_page=True)

        # Return objects needed for axe run (we'll re-use the same page if desired)
        # For simplicity, axe is run in a separate helper (caller can keep same page)
        html = await page.content()
        await context.close()
        await browser.close()
        return {"html": html}
