"""
API routes for Patient management:
- List pending and admitted patients
- Admit new patient
- Bulk generate synthetic patients for live testing
- Reset patients
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random

from app.database import get_db
from app.models import Patient, Bed
from app.schemas import PatientCreate, PatientOut

router = APIRouter(prefix="/api/patients", tags=["Patients"])

NAMES = ["Aarav", "Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Neha", 
         "Karan", "Pooja", "Arjun", "Kavita", "Siddharth", "Meera", "Aditya", "Riya"]
SURNAMES = ["Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Singh", "Kumar", "Rao"]
SPECIALTIES = ["Cardiology", "Neurology", "Orthopedics", "Oncology", "Pulmonology"]
BED_TYPES = ["ICU", "Telemetry", "Isolation", "Standard"]

@router.get("/", response_model=List[PatientOut])
def get_patients(db: Session = Depends(get_db), limit: int = 100):
    return db.query(Patient).order_by(Patient.id.desc()).limit(limit).all()

@router.post("/", response_model=PatientOut)
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(
        name=patient_in.name,
        age=patient_in.age,
        gender=patient_in.gender,
        acuity=patient_in.acuity,
        specialty=patient_in.specialty,
        bed_type_needed=patient_in.bed_type_needed,
        preferred_slot=patient_in.preferred_slot,
        status="Pending",
        match_score=0.0
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.post("/generate-sample")
def generate_sample_patients(count: int = 25, db: Session = Depends(get_db)):
    created = []
    for _ in range(count):
        p = Patient(
            name=f"{random.choice(NAMES)} {random.choice(SURNAMES)}",
            age=random.randint(18, 85),
            gender=random.choice(["Male", "Female", "Other"]),
            acuity=random.choices([1, 2, 3, 4, 5], weights=[0.2, 0.3, 0.25, 0.15, 0.1])[0],
            specialty=random.choice(SPECIALTIES),
            bed_type_needed=random.choices(BED_TYPES, weights=[0.15, 0.25, 0.1, 0.5])[0],
            preferred_slot=random.choice([1, 2, 3, 4]),
            status="Pending",
            match_score=0.0
        )
        db.add(p)
        created.append(p)
    db.commit()
    return {"message": f"Successfully generated {count} pending patient admission requests."}

@router.delete("/clear")
def clear_patients(db: Session = Depends(get_db)):
    # Unlink beds first
    db.query(Bed).update({"is_occupied": False})
    deleted = db.query(Patient).delete()
    db.commit()
    return {"message": f"Cleared {deleted} patients and freed all beds."}
