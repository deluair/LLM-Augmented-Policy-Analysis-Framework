"""
Main entry point for the LLM Policy Analysis API.

Initializes the FastAPI application and includes routers.
"""

from fastapi import FastAPI

# Import routers from endpoints module
from .endpoints import (
    central_bank_router,
    earnings_router,
    policy_analysis_router,
    quantification_router,
    retrieval_router
)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Policy Analysis API",
    description="API for analyzing policy documents using LLMs.",
    version="0.1.0"
)

@app.get("/", tags=["Status"])
def read_root():
    """Root endpoint providing basic API status."""
    return {"message": "Welcome to the LLM Policy Analysis API"}

# Include endpoint routers
app.include_router(central_bank_router)
app.include_router(earnings_router)
app.include_router(policy_analysis_router)
app.include_router(quantification_router)
app.include_router(retrieval_router)

# Placeholder for potential startup/shutdown events if needed
# @app.on_event("startup")
# async def startup_event():
#     print("Starting up API...")

# @app.on_event("shutdown")
# async def shutdown_event():
#     print("Shutting down API...")
