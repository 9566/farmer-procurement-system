"""
Database configuration for the Smart Farmer Procurement System.
Uses MySQL with SQLAlchemy.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")
load_dotenv()


# ============================================================
# DATABASE VARIABLES
# ============================================================

DB_USER = os.getenv("DB_USER") or os.getenv("MYSQLUSER")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD")
DB_HOST = os.getenv("DB_HOST") or os.getenv("MYSQLHOST")
DB_PORT = os.getenv("DB_PORT") or os.getenv("MYSQLPORT") or "3306"
DB_NAME = (
    os.getenv("DB_NAME")
    or os.getenv("MYSQLDATABASE")
    or "farmer_procurement"
)


# ============================================================
# VALIDATION
# ============================================================

# Skipped for sqlite


# ============================================================
# DATABASE URL
# Auto-detects: uses MySQL if DB_HOST is set, else SQLite (local dev)
# ============================================================

if DB_HOST and DB_USER and DB_PASSWORD:
    # ---- Production: MySQL ----
    DATABASE_URL = (
        f"mysql+pymysql://"
        f"{quote_plus(DB_USER)}:"
        f"{quote_plus(DB_PASSWORD)}@"
        f"{DB_HOST}:"
        f"{DB_PORT}/"
        f"{quote_plus(DB_NAME)}"
    )
    print("Database: Using MySQL (production)")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=280,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        future=True,
        echo=False,
    )
else:
    # ---- Local Dev: SQLite ----
    DATABASE_URL = "sqlite:///./farmer_procurement.db"
    print("Database: Using SQLite (local dev)")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
        echo=False,
    )


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# BASE
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():
    Base.metadata.create_all(bind=engine)