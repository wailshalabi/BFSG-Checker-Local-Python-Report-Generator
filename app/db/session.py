from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.models import Base

_engine = None
SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        # check_same_thread needed for SQLite with worker+api
        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        _engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
    return _engine

def init_db():
    global SessionLocal
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

def get_session():
    if SessionLocal is None:
        init_db()
    return SessionLocal()
