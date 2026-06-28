"""Pydantic models for TD Compass domain objects."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

CompetencyLevel = Literal["E1", "E2"]
CertType = Literal["Internal", "External"]
ItemStatus = Literal["Active", "Expiring Soon", "Expired"]


class LearningHours(BaseModel):
    year: int
    quarter: str  # Q1..Q4
    hours: float
    target_hours: float


class Certification(BaseModel):
    name: str
    provider: str
    type: CertType
    completed_date: str  # ISO date
    expiry_date: Optional[str]  # ISO date or None if it never expires
    status: ItemStatus
    days_to_expiry: Optional[int]


class Competency(BaseModel):
    name: str
    category: str
    level: CompetencyLevel
    acquired_date: str
    expiry_date: Optional[str]
    status: ItemStatus
    days_to_expiry: Optional[int]


class Associate(BaseModel):
    id: str
    name: str
    email: str
    designation: str
    band: str
    department: str
    project: str
    project_manager: str
    td_manager: str
    location: str
    date_of_joining: str
    total_experience_years: float
    performance_rating: str
    learning_hours: list[LearningHours]
    certifications: list[Certification]
    competencies: list[Competency]
    upcoming_td_programs: list["TDProgram"]
    # Derived rollups
    ytd_learning_hours: float
    ytd_target_hours: float
    e1_competencies: int
    e2_competencies: int


class TDProgram(BaseModel):
    name: str
    category: str
    start_date: str
    mode: str  # Classroom / Virtual / Self-paced
    duration_days: int
    status: str  # Nominated / Confirmed / Waitlisted / Recommended


class Policy(BaseModel):
    id: str
    title: str
    category: str
    body: str


Associate.model_rebuild()
