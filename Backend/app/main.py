import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.database import engine, Base
from app.api import api_router

# Configure Logger without exposing full phone numbers or PII
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nxtwave_growth_backend")

# Create database tables automatically on startup if using SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NxtWave Growth Challenge API",
    description="Measurement & Growth REST API layer for NxtWave Growth Intern Challenge",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router for /api/v1, /v1, and root
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/v1")
app.include_router(api_router)

@app.get("/", include_in_schema=False)
def root():
    return {
        "title": "NxtWave Growth Challenge API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Safe Error Responses (Never expose stack traces in production)
@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    if settings.APP_ENV == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."}
    )

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

from fastapi.encoders import jsonable_encoder

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())}
    )
