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
from fillscheduler.api.websocket import router as websocket_router

# Create FastAPI application with comprehensive OpenAPI configuration
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
    # OpenAPI metadata
    contact={
        "name": "Filling Scheduler Team",
        "url": "https://github.com/vikas-py/filling_scheduler",
        "email": "support@fillscheduler.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    # Enhanced OpenAPI tags with descriptions
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and authorization operations. Includes login, token refresh, and user management.",
        },
        {
            "name": "schedules",
            "description": "Schedule creation, retrieval, and management. Create optimized production schedules using various strategies.",
        },
        {
            "name": "comparisons",
            "description": "Strategy comparison operations. Compare multiple scheduling strategies side-by-side to find the best approach.",
        },
        {
            "name": "configuration",
            "description": "Configuration template management. Create, update, and manage scheduling configuration templates.",
        },
        {
            "name": "websocket",
            "description": "Real-time WebSocket connections. Subscribe to schedule and comparison progress updates in real-time.",
        },
    ],
    # Additional OpenAPI customization
    terms_of_service="https://github.com/vikas-py/filling_scheduler/blob/main/LICENSE",
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server",
        },
        {
            "url": "https://api.fillscheduler.example.com",
            "description": "Production server",
        },
    ],
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
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
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
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
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
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with detailed messages."""
    print(f"❌ Validation error in {request.method} {request.url}:")
    print(f"   {exc.errors()}")

    # Convert body to string if it's bytes (e.g., multipart form data)
    body_content = exc.body
    if isinstance(body_content, bytes):
        try:
            body_content = body_content.decode("utf-8")
            # Truncate if too long (multipart form data can be huge)
            if len(body_content) > 500:
                body_content = body_content[:500] + "... (truncated)"
        except UnicodeDecodeError:
            body_content = "<binary data>"

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": body_content,
            "message": "Validation error. Check the 'detail' field for specific errors.",
        },
    )


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
app.include_router(websocket_router.router, prefix="/api/v1", tags=["websocket"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fillscheduler.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
