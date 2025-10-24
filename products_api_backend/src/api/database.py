import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Determine database URL from environment or fallback to local SQLite.
# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Return the database URL to connect to.

    Tries to use products_database env var if present; otherwise falls back to SQLite file.
    """
    # Common env var names that might be set by the dependency container
    candidates = [
        "PRODUCTS_DATABASE_URL",
        "PRODUCTS_DB_URL",
        "DATABASE_URL",
        "MYSQL_URL",  # in case dependency provides this generic variable
        "POSTGRES_URL",
    ]
    for key in candidates:
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()

    # Fallback to local SQLite database file
    data_dir = os.getenv("DATA_DIR", "/data")
    os.makedirs(data_dir, exist_ok=True)
    return f"sqlite:///{os.path.join(data_dir, 'products.db')}"

DATABASE_URL = get_database_url()

# Configure SQLAlchemy engine and session factory.
# For SQLite, need check_same_thread=False in many FastAPI single-process contexts.
engine_args = {}
if DATABASE_URL.startswith("sqlite:///"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy Session and ensures proper close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for working with a transactional session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# PUBLIC_INTERFACE
def init_db(seed: bool = True) -> None:
    """Create database tables and optionally seed demo data."""
    # Local import to avoid circular deps
    from .models import Product  # noqa: WPS433

    Base.metadata.create_all(bind=engine)

    if not seed:
        return

    # Seed minimal demo data if table is empty
    with session_scope() as s:
        has_any = s.query(Product).first()
        if has_any:
            return
        sample = [
            Product(name="Notebook", price=4.99, quantity=120),
            Product(name="Ballpoint Pen", price=1.49, quantity=500),
            Product(name="Desk Chair", price=89.99, quantity=35),
        ]
        s.add_all(sample)
