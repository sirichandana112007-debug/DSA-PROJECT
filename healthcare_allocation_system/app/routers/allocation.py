"""
API routes for running Allocation algorithms:
- Execute allocation on pending patients with chosen algorithm
- Record allocation logs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.database import get_db
from app.models import Patient, Bed, AllocationLog
from app.schemas import AllocationRequest, AllocationSummary
from app.algorithms import (
    allocate_fcfs,
    allocate_greedy,
    allocate_exact_match,
    allocate_our_pipeline
)

router = APIRouter(prefix="/api/allocation", tags=["Allocation Engine"])

@router.post("/run", response_model=AllocationSummary)
def run_allocation(request: AllocationRequest, db: Session = Depends(get_db)):
    pending_patients = db.query(Patient).filter(Patient.status == "Pending").all()
    available_beds = db.query(Bed).filter(Bed.is_occupied == False).all()
    
    if not pending_patients:
        raise HTTPException(status_code=400, detail="No pending patient admission requests found. Please add or generate patients first.")
        
    if not available_beds:
        raise HTTPException(status_code=400, detail="No free beds available in the hospital inventory.")
        
    strategy = request.strategy.lower()
    
    # Select corresponding algorithm implementation
    if strategy in ["manual_fcfs", "fcfs"]:
        allocations = allocate_fcfs(pending_patients, available_beds)
        strat_display = "Manual / FCFS"
    elif strategy in ["greedy", "greedy_only"]:
        allocations = allocate_greedy(pending_patients, available_beds)
        strat_display = "Greedy only"
    elif strategy in ["exact_match", "exact_match_only"]:
        allocations = allocate_exact_match(pending_patients, available_beds)
        strat_display = "Exact match only"
    elif strategy in ["our_pipeline", "proposed_pipeline", "pipeline"]:
        allocations = allocate_our_pipeline(pending_patients, available_beds, batch_size=request.batch_size or 50)
        strat_display = "Our pipeline"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: '{request.strategy}'")
        
    # Apply allocations to database
    total_score = 0.0
    for alloc in allocations:
        p_id = alloc["patient_id"]
        b_id = alloc["bed_id"]
        score = alloc["match_score"]
        
        patient = db.query(Patient).filter(Patient.id == p_id).first()
        bed = db.query(Bed).filter(Bed.id == b_id).first()
        
        if patient and bed:
            patient.status = "Allocated"
            patient.allocated_bed_id = bed.id
            patient.match_score = score
            bed.is_occupied = True
            total_score += score
            
    # Mark remaining unallocated as waitlisted
    remaining = db.query(Patient).filter(Patient.status == "Pending").all()
    for rem in remaining:
        rem.status = "Waitlisted"
        
    db.commit()
    
    # Calculate statistics
    total_reqs = len(pending_patients)
    admitted_count = len(allocations)
    admission_rate = round((admitted_count / total_reqs) * 100, 1) if total_reqs > 0 else 0.0
    
    total_hospital_beds = db.query(Bed).count()
    occupied_now = db.query(Bed).filter(Bed.is_occupied == True).count()
    bed_util = round((occupied_now / total_hospital_beds) * 100, 1) if total_hospital_beds > 0 else 0.0
    
    avg_match_quality = round((total_score / admitted_count) * 100, 1) if admitted_count > 0 else 0.0
    
    # Save audit log
    log = AllocationLog(
        strategy=strat_display,
        total_requests=total_reqs,
        admitted_count=admitted_count,
        match_rate=avg_match_quality,
        bed_utilization=bed_util,
        admission_rate=admission_rate
    )
    db.add(log)
    db.commit()
    
    return AllocationSummary(
        strategy=strat_display,
        total_requests=total_reqs,
        admitted_count=admitted_count,
        admission_rate_percent=admission_rate,
        bed_utilization_percent=bed_util,
        match_rate_percent=avg_match_quality,
        execution_message=f"Successfully allocated {admitted_count} patients using {strat_display}."
    )
