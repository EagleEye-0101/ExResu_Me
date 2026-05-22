from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from resume_engine.config import settings
from resume_engine.db.models import Base

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        db_url = settings.database_url
        if db_url.startswith("sqlite:///./"):
            path = Path(db_url.replace("sqlite:///./", ""))
            path.parent.mkdir(parents=True, exist_ok=True)
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(db_url, connect_args=connect_args)
    return _engine


def get_db():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_columns(engine):
    """Add new columns to existing SQLite DBs."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "resumes" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("resumes")}
    alters = []
    if "title" not in cols:
        alters.append("ALTER TABLE resumes ADD COLUMN title VARCHAR(300) DEFAULT ''")
    if "status" not in cols:
        alters.append("ALTER TABLE resumes ADD COLUMN status VARCHAR(20) DEFAULT 'finished'")
    if "draft_json" not in cols:
        alters.append("ALTER TABLE resumes ADD COLUMN draft_json TEXT DEFAULT ''")
    if "wizard_step" not in cols:
        alters.append("ALTER TABLE resumes ADD COLUMN wizard_step INTEGER DEFAULT 0")
    with engine.connect() as conn:
        for sql in alters:
            conn.execute(text(sql))
        conn.commit()


def init_db():
    global _SessionLocal
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)
    _migrate_columns(engine)
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
