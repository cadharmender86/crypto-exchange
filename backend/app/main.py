from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting BitNova Exchange API...")

    yield

    print("Shutting down BitNova Exchange API...")
    await close_database()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        response = await call_next(request)

        # Prevent MIME-type sniffing
        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        # Prevent clickjacking
        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        # Restrict browser referrer information
        response.headers[
            "Referrer-Policy"
        ] = "no-referrer"

        # Basic Content Security Policy
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'"
        )

        # HSTS should only be enabled when the API is
        # actually served through HTTPS.
        if request.url.scheme == "https":
            response.headers[
                "Strict-Transport-Security"
            ] = (
                "max-age=31536000; "
                "includeSubDomains"
            )

        return response

is_production = (
    settings.environment.strip().lower()
    == "production"
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend API for the BitNova digital asset exchange."
    ),
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
    lifespan=lifespan,
)


# ============================================================
# SECURITY HEADERS
# ============================================================

app.add_middleware(
    SecurityHeadersMiddleware
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }