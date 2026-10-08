"""
API routes for Review 3 Analytics & Comparative Benchmarks:
- Return benchmark results matching Review 3 graphs
- Retrieve allocation logs
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import AllocationLog
from app.algorithms import run_comparative_simulation

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Review 3"])

@router.get("/benchmark")
def get_benchmark_comparison(records: int = 10000):
    """
    Returns comparative evaluation data across all 4 strategies (for 10,000 records).
    Directly powers the Review 3 bar chart on the frontend dashboard.
    """
    return run_comparative_simulation(num_records=records)

@router.get("/logs")
def get_allocation_history(db: Session = Depends(get_db)):
    return db.query(AllocationLog).order_by(AllocationLog.id.desc()).limit(10).all()
