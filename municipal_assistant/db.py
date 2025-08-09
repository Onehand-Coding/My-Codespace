from __future__ import annotations
from pathlib import Path
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = Path("data/municipal.db")
DB_URL = f"sqlite:///{DB_PATH}"

def ensure_db_dir() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(DB_URL, echo=False)


def init_db() -> None:
    ensure_db_dir()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
