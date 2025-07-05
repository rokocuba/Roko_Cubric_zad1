"""
Glavna FastAPI aplikacija za TicketHub

Autor: Roko Čubrić (roko.cubric@fer.hr)
AI Akademija 2025 - Python Developer Test

Generated with AI assistance - GitHub Copilot
Razlog: Standardni boilerplate za FastAPI aplikaciju s osnovnom strukturom i lifecycle management
Prompt: "Kreiraj FastAPI main.py s health check endpointom, CORS middleware i async lifecycle management"
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager za startup i shutdown događaje"""
    # Startup
    print("Starting TicketHub API...")

    yield

    # Shutdown
    print("Shutting down TicketHub API...")
    # Zatvori HTTP klijente
    from .services.external_api import dummy_json_service, ticket_transform_service

    await dummy_json_service.close()
    if hasattr(ticket_transform_service, "dummy_json_service"):
        await ticket_transform_service.dummy_json_service.close()


# Kreiranje FastAPI aplikacije
app = FastAPI(
    title="TicketHub API",
    description="Support Ticket Management REST API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # U produkciji ograničiti na specifične domene
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - osnovne informacije o API-ju"""
    return {
        "message": "Welcome to TicketHub API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint za monitoring i container orchestration"""
    return {"status": "healthy", "service": "tickethub-api", "version": "0.1.0"}


# Uključi ticket routes
from .api import tickets

app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
