from pydantic import BaseModel
from datetime import datetime

class EventIdeaCreate(BaseModel):
    title: str
    min_headcount: int
    max_headcount: int
    duration_min: int
    budget_pp: float | None = None
    extra_details: str | None = None
    description: str | None = None

class EventIdeaOut(BaseModel):
    id: int
    creator_id: int 
    title: str
    min_headcount: int
    max_headcount: int
    duration_min: int
    created_at: datetime 
    budget_pp: float | None = None
    extra_details: str | None = None
    description: str | None = None
    