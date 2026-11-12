"""Database connection and session lifecycle management."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from config import Config

Base = declarative_base()

_engine = None
_SessionFactory = None
_scoped_session = None


def get_engine(db_uri: str = None):
    """Retrieve or initialize the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        uri = db_uri or Config.SQLALCHEMY_DATABASE_URI
        # Ensure database directory exists for SQLite
        if uri.startswith("sqlite:///"):
            db_path = uri.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            _engine = create_engine(
                uri,
                connect_args={"check_same_thread": False},
                echo=False
            )
        else:
            _engine = create_engine(uri, echo=False)
    return _engine


def get_db_session():
    """Retrieve a thread-safe scoped database session."""
    global _SessionFactory, _scoped_session
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        _scoped_session = scoped_session(_SessionFactory)
    return _scoped_session()


def init_db(app=None, db_uri: str = None):
    """Create all tables in the database if they do not exist."""
    engine = get_engine(db_uri)
    from . import models  # Ensure models are imported before create_all
    Base.metadata.create_all(bind=engine)
    return engine
