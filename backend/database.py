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
# ============================================================

DATABASE_URL = "sqlite:///./farmer_procurement.db"


# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

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