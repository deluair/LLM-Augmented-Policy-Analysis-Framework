"""
API Error Handling Utilities.

Defines custom exception handlers for FastAPI to ensure consistent JSON error responses.
"""

import logging
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

# If using Pydantic v2, ValidationError is imported differently
try:
    from pydantic.v1 import ValidationError
except ImportError:
    from pydantic import ValidationError

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """Registers custom exception handlers with the FastAPI application."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handles FastAPI's built-in HTTPException."""
        logger.warning(f"HTTP Exception: {exc.status_code} {exc.detail} for {request.method} {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handles validation errors for request data (Pydantic models)."""
        error_details = exc.errors()
        logger.warning(f"Request Validation Error: {error_details} for {request.method} {request.url.path}")
        # Provide more structured error details if desired
        simplified_errors = []
        for error in error_details:
            field = ".".join(map(str, error['loc'])) if error.get('loc') else 'unknown_field'
            simplified_errors.append({"field": field, "message": error['msg']})
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation Error", "errors": simplified_errors},
        )
    
    # Handle Pydantic ValidationErrors that might occur outside request validation
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handles Pydantic validation errors occurring outside request validation."""
        logger.error(f"Internal Pydantic Validation Error: {exc.errors()} (potentially during response modeling) for {request.method} {request.url.path}", exc_info=True)
        # For internal errors, often best to return a generic 500
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error: Data validation failed during processing."}, 
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handles any other unhandled exceptions (catch-all)."""
        logger.error(f"Unhandled Exception: {type(exc).__name__}: {exc} for {request.method} {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )

    logger.info("Custom FastAPI exception handlers registered.")

# Example of how to use this in main.py:
# from fastapi import FastAPI
# from .utils.error_handling import setup_exception_handlers
# 
# app = FastAPI()
# setup_exception_handlers(app)
# 
# # ... rest of your app setup ...
