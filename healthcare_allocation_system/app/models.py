"""
SQLAlchemy ORM Data Models for Healthcare Resource Allocation System.
Represents entities identified in Project Reviews:
- Patient (clinical attributes, triage score, requirements)
- Bed (specialty, care level, availability status)
- Doctor (department, on-duty status)
- AllocationLog (audit log of allocation runs and metrics)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    acuity = Column(Integer, default=3)  # 1 (lowest) to 5 (critical emergency)
    specialty = Column(String)           # e.g., Cardiology, Oncology, Neurology
    bed_type_needed = Column(String)     # ICU, Telemetry, Isolation, Standard
    preferred_slot = Column(Integer, default=1) # 1: Morning, 2: Afternoon, 3: Evening, 4: Night
    status = Column(String, default="Pending")  # Pending, Allocated, Waitlisted, Discharged
    match_score = Column(Float, default=0.0)
    allocated_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)
    arrival_time = Column(DateTime, default=datetime.utcnow)

    allocated_bed = relationship("Bed", back_populates="current_patient")

class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    bed_number = Column(String, unique=True, index=True)
    department = Column(String)          # Cardiology, Neurology, Orthopedics, etc.
    bed_type = Column(String)            # ICU, Telemetry, Isolation, Standard
    slot = Column(Integer, default=1)
    is_occupied = Column(Boolean, default=False)

    current_patient = relationship("Patient", back_populates="allocated_bed", uselist=False)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    department = Column(String)
    specialization = Column(String)
    is_on_duty = Column(Boolean, default=True)

class AllocationLog(Base):
    __tablename__ = "allocation_logs"

    id = Column(Integer, primary_key=True, index=True)
    strategy = Column(String)            # Manual_FCFS, Greedy_Only, Exact_Match_Only, Proposed_Pipeline
    total_requests = Column(Integer)
    admitted_count = Column(Integer)
    match_rate = Column(Float)
    bed_utilization = Column(Float)
    admission_rate = Column(Float)
    executed_at = Column(DateTime, default=datetime.utcnow)
