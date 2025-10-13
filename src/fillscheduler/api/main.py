"""
Main FastAPI application.

Entry point for the Filling Scheduler API.
"""

import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fillscheduler.api.config import settings
from fillscheduler.api.database.session import init_db
from fillscheduler.api.routers import auth, comparison, config, schedule

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🌐 CORS origins: {', '.join(settings.CORS_ORIGINS)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print(f"👋 {settings.APP_NAME} shutting down...")


# Add exception handlers for debugging


# FIX Bug #7: Rollback database transaction on HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with automatic database rollback.

    This prevents partial database changes from being committed
    when validation fails or other HTTP errors occur.
    """
    # Rollback any pending database transactions
    # The db session is injected per-request, stored in request.state
    if hasattr(request.state, "db"):
        try:
            request.state.db.rollback()
            print(f"🔄 Rolled back database transaction for {request.method} {request.url}")
        except Exception as rollback_error:
            print(f"⚠️ Error during rollback: {rollback_error}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and return detailed error."""
    # Also rollback on unexpected exceptions
    if hasattr(request.state, "db"):
        try:
            request.state.db.rollback()
        except Exception:
            pass  # Ignore rollback errors for unexpected exceptions

    print(f"❌ Exception in {request.method} {request.url}:")
    print(f"   {type(exc).__name__}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__, "path": str(request.url)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    print(f"❌ Validation error in {request.method} {request.url}:")
    print(f"   {exc}")
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Add routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(schedule.router, prefix="/api/v1", tags=["schedules"])
app.include_router(comparison.router, prefix="/api/v1", tags=["comparisons"])
app.include_router(config.router, prefix="/api/v1", tags=["configuration"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fillscheduler.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
