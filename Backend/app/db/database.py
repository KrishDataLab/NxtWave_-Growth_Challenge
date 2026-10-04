import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("nxtwave_growth_backend")

db_url = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("POSTGRES_URL")
    or os.environ.get("POSTGRES_PRISMA_URL")
    or settings.DATABASE_URL
)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        if "./" in db_url:
            db_url = "sqlite:////tmp/nxtwave_growth.db"

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )
except Exception as err:
    logger.warning(f"Primary DB driver engine creation failed ({err}), trying fallback...")
    try:
        if "postgresql" in db_url:
            fallback_url = db_url.replace("postgresql+psycopg2://", "postgresql+pg8000://").replace("postgresql://", "postgresql+pg8000://")
            engine = create_engine(fallback_url, pool_pre_ping=True)
        else:
            engine = create_engine("sqlite:////tmp/nxtwave_growth.db", connect_args={"check_same_thread": False})
    except Exception as fallback_err:
        logger.error(f"Fallback DB engine creation failed ({fallback_err}), reverting to writable SQLite /tmp")
        engine = create_engine("sqlite:////tmp/nxtwave_growth.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
