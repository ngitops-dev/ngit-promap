from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.v1.health import router as health_router
from backend.api.v1.payments import router as payments_router
from backend.api.v1.programs import router as programs_router
from backend.api.v1.registrations import router as registrations_router
from backend.api.v1.webhooks import router as webhooks_router
from backend.config import settings
from backend.utils.logging import generate_request_id, get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.LOG_LEVEL)
    logger.info("NGiT Backend starting | env=%s", settings.APP_ENV)
    yield
    logger.info("NGiT Backend shutting down")


app = FastAPI(
    title="NGiT Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled exception | request_id=%s | error=%s",
        request_id,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            },
        },
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
async def root():
    return {
        "name": "NGiT Platform API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "environment": settings.APP_ENV,
    }


app.include_router(health_router, tags=["Health"])
app.include_router(webhooks_router, prefix="/api/v1", tags=["Webhooks"])
app.include_router(programs_router, prefix="/api/v1", tags=["Programs"])
app.include_router(registrations_router, prefix="/api/v1", tags=["Registrations"])
app.include_router(payments_router, prefix="/api/v1", tags=["Payments"])
