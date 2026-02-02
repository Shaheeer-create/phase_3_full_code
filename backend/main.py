"""
TodoAI Backend API - FastAPI Application

Main application entry point with CORS, database initialization, and routing.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routers import tasks, conversations, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs on startup and shutdown.
    """
    # Startup: Initialize database tables
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully")

    yield

    # Shutdown: Cleanup if needed
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="TodoAI API",
    version="1.0.0",
    description="Backend API for TodoAI - Full-Stack Todo Application with AI Chat",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)  # Auth router (no /api prefix)
app.include_router(tasks.router)
app.include_router(conversations.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "TodoAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
