import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("nxtwave_growth_backend")

db_url = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("POSTGRES_URL")
    or os.environ.get("POSTGRES_PRISMA_URL")
    or settings.DATABASE_URL
)

def format_db_url(raw_url: str) -> str:
    url = raw_url
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        if "postgresql+" not in url:
            driver = "postgresql+pg8000://"
            if url.startswith("postgres://"):
                url = url.replace("postgres://", driver, 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", driver, 1)
        if "postgresql" in url and "sslmode" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}sslmode=require"
    return url

db_url = format_db_url(db_url)

if db_url.startswith("sqlite"):
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        if "./" in db_url:
            db_url = "sqlite:////tmp/nxtwave_growth.db"

def create_configured_engine(target_url: str):
    c_args = {}
    if target_url.startswith("sqlite"):
        c_args = {"check_same_thread": False}
    return create_engine(target_url, connect_args=c_args, pool_pre_ping=True)

try:
    engine = create_configured_engine(db_url)
except Exception as err:
    logger.warning(f"Primary DB engine creation failed ({err}), falling back to SQLite /tmp")
    db_url = "sqlite:////tmp/nxtwave_growth.db"
    engine = create_configured_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_tables_created = False

def init_db_schema():
    global _tables_created, engine, SessionLocal
    if _tables_created:
        return
    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            if "postgresql" in str(engine.url):
                for col_def in [
                    "ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE",
                    "ADD COLUMN IF NOT EXISTS whatsapp_opt_in BOOLEAN DEFAULT FALSE",
                    "ADD COLUMN IF NOT EXISTS verification_id VARCHAR(64)",
                    "ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE"
                ]:
                    try:
                        conn.execute(text(f"ALTER TABLE registrations {col_def}"))
                    except Exception:
                        pass

            # Safe DDL migration: Guarantee unique indexes exist on email & referral_code
            for idx_sql in [
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_registrations_email ON registrations (email)",
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_registrations_referral_code ON registrations (referral_code)"
            ]:
                try:
                    conn.execute(text(idx_sql))
                except Exception as idx_err:
                    logger.warning(f"Index creation notice: {idx_err}")

        _tables_created = True
    except Exception as err:
        logger.warning(f"Primary DB connection/schema creation failed ({err}), switching to fallback SQLite /tmp...")
        try:
            fallback_url = "sqlite:////tmp/nxtwave_growth.db"
            engine = create_configured_engine(fallback_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
            with engine.begin() as conn:
                for idx_sql in [
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_registrations_email ON registrations (email)",
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_registrations_referral_code ON registrations (referral_code)"
                ]:
                    try:
                        conn.execute(text(idx_sql))
                    except Exception:
                        pass
            _tables_created = True
        except Exception as fb_err:
            logger.error(f"Fallback DB initialization failed: {fb_err}")

def get_db():
    init_db_schema()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
