# =========================
# DATABASE CONFIG
# =========================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# SQLite database URL
DATABASE_URL = "sqlite:///./spendiq.db"


# =========================
# ENGINE
# =========================

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)


# =========================
# SESSION
# =========================

# Session factory (used in dependencies)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================
# BASE MODEL
# =========================

# Base class for all models
Base = declarative_base()