"""
API routes for Hospital Resource management:
- List beds and availability
- Initialize/Seed hospital bed inventory across departments
- Free beds / Discharge
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Bed, Doctor
from app.schemas import BedOut

router = APIRouter(prefix="/api/resources", tags=["Resources"])

DEFAULT_DEPARTMENTS = [
    ("Cardiology", 8),
    ("Neurology", 6),
    ("Orthopedics", 6),
    ("Oncology", 6),
    ("Pulmonology", 6),
]

BED_TYPES = ["ICU", "Telemetry", "Isolation", "Standard"]

@router.get("/beds", response_model=List[BedOut])
def get_beds(db: Session = Depends(get_db)):
    return db.query(Bed).all()

@router.get("/summary")
def get_resource_summary(db: Session = Depends(get_db)):
    total_beds = db.query(Bed).count()
    occupied_beds = db.query(Bed).filter(Bed.is_occupied == True).count()
    free_beds = total_beds - occupied_beds
    utilization = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0
    
    return {
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
        "free_beds": free_beds,
        "utilization_percent": utilization
    }

@router.post("/seed-defaults")
def seed_default_inventory(db: Session = Depends(get_db)):
    """Populates initial realistic hospital beds across specialties if table is empty"""
    existing_count = db.query(Bed).count()
    if existing_count > 0:
        return {"message": f"Inventory already contains {existing_count} beds."}
        
    created_beds = 0
    bed_counter = 101
    
    for dept, count in DEFAULT_DEPARTMENTS:
        for i in range(count):
            # Assign bed types based on clinical care tiers
            if i < 2:
                b_type = "ICU"
            elif i < 4:
                b_type = "Telemetry"
            elif i < 5:
                b_type = "Isolation"
            else:
                b_type = "Standard"
                
            slot = (i % 4) + 1
            bed = Bed(
                bed_number=f"{dept[:3].upper()}-{bed_counter}",
                department=dept,
                bed_type=b_type,
                slot=slot,
                is_occupied=False
            )
            db.add(bed)
            bed_counter += 1
            created_beds += 1
            
    db.commit()
    return {"message": f"Successfully initialized {created_beds} hospital beds across 5 departments."}

@router.post("/reset-beds")
def reset_bed_occupancy(db: Session = Depends(get_db)):
    db.query(Bed).update({"is_occupied": False})
    db.commit()
    return {"message": "All beds have been marked as free/unoccupied."}
