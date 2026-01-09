from fastapi import FastAPI
from app.api.routes import router as api_router
from app.ui.routes import router as ui_router
from app.db.session import init_db

app = FastAPI(title="BFSG Checker", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router)
app.include_router(ui_router)
