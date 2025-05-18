"""
Main FastAPI application file for the Agentic Character Chatbot backend.
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import os
import sys
from pathlib import Path

# Add parent directory to sys.path for relative imports
sys.path.append(str(Path(__file__).parent.parent))

# Import configuration
from app.core.config import settings

# Import API router
from app.api.v1.api import api_router

# Initialize FastAPI app with metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Set up custom API documentation
from app.core.api_docs import setup_api_docs
setup_api_docs(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware components
from app.core.middleware import RequestLoggingMiddleware, RateLimitingMiddleware

# Add rate limiting middleware (if enabled)
if settings.RATE_LIMIT_PER_MINUTE > 0:
    app.add_middleware(RateLimitingMiddleware)

# Add request logging middleware (if enabled)
if settings.ENABLE_LOGGING:
    app.add_middleware(RequestLoggingMiddleware)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {
        "status": "ok",
        "message": f"Welcome to {settings.PROJECT_NAME}!",
        "version": settings.VERSION,
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify system status.
    """
    return {
        "status": "ok",
        "api_version": settings.VERSION,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }

# Import error models
from app.core.error_models import ErrorResponse, ValidationErrorResponse, NotFoundErrorResponse

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors and return standardized error responses.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(
            message="Validation error",
            details=exc.errors()
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Standardize HTTP exception responses.
    """
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=exc.status_code,
            content=NotFoundErrorResponse(
                message=exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", str(exc.detail))
            ).dict()
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", str(exc.detail)),
                details=None if isinstance(exc.detail, str) else exc.detail.get("details", None)
            ).dict()
        )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unhandled exceptions and return standardized error responses.
    """
    # Log the exception
    import traceback
    traceback.print_exc()
    
    # Return a 500 error with a generic message in production
    # and a more detailed message in development
    if settings.DEBUG_MODE:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="Internal server error",
                details=str(exc)
            ).dict()
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="Internal server error"
            ).dict()
        )

# Register API routes
app.include_router(api_router)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
