"""
FastAPI Main Application Entrypoint:
- Initializes database schema
- Mounts REST API routers
- Serves the Interactive Browser Frontend Dashboard
- Auto-seeds initial hospital resources
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import engine, Base, SessionLocal
from app.models import Bed
from app.routers import patients, resources, allocation, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Resource Allocation & Appointment Optimization API",
    description="Automated patient triage, bed management, and priority bipartite matching system.",
    version="1.0.0"
)

# CORS middleware for open accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(patients.router)
app.include_router(resources.router)
app.include_router(allocation.router)
app.include_router(analytics.router)

# Locate static directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend_dashboard():
    """Serves the interactive web browser dashboard"""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Healthcare Allocation API running. Access /docs for Swagger API documentation."}

@app.on_event("startup")
def startup_event():
    """Auto-seed initial hospital beds on first launch if table is empty"""
    db = SessionLocal()
    try:
        count = db.query(Bed).count()
        if count == 0:
            from app.routers.resources import seed_default_inventory
            seed_default_inventory(db)
            print("[INFO] Initialized default hospital bed inventory.")
    finally:
        db.close()
