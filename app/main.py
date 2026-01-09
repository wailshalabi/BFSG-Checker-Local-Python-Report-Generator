from fastapi import FastAPI
from app.config import settings
from app.api.routes import router
from app.db.session import init_db

app = FastAPI(title="BFSG Checker", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router)
