"""
Pydantic schemas for data validation and API request/response serialization.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    acuity: int
    specialty: str
    bed_type_needed: str
    preferred_slot: int

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    id: int
    status: str
    match_score: float
    allocated_bed_id: Optional[int] = None
    arrival_time: datetime
    model_config = ConfigDict(from_attributes=True)

class BedBase(BaseModel):
    bed_number: str
    department: str
    bed_type: str
    slot: int
    is_occupied: bool = False

class BedCreate(BedBase):
    pass

class BedOut(BedBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AllocationRequest(BaseModel):
    strategy: str  # "manual_fcfs", "greedy", "exact_match", "our_pipeline"
    batch_size: Optional[int] = 50

class AllocationSummary(BaseModel):
    strategy: str
    total_requests: int
    admitted_count: int
    admission_rate_percent: float
    bed_utilization_percent: float
    match_rate_percent: float
    execution_message: str

class BenchmarkRequest(BaseModel):
    num_records: int = 1000  # Default 1000, customizable up to 10000
