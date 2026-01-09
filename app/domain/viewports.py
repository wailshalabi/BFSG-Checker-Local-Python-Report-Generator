from app.config import settings

def get_viewports():
    return [
        {"name": "desktop", "width": settings.desktop_width, "height": settings.desktop_height},
        {"name": "mobile", "width": settings.mobile_width, "height": settings.mobile_height},
    ]
