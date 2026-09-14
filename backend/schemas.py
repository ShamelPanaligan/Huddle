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

class UserRegister(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MatchRequest(BaseModel):
    headcount: int
    available_min: int 
    budget_cap: float | None = None

class EventOccurrenceCreate(BaseModel):
    idea_id: int
    proposed_time: datetime

class EventOccurrenceOut(BaseModel):
    id: int
    idea_id: int
    proposed_time: datetime
    created_by: int
    created_at: datetime

class VoteCreate(BaseModel):
    voter_token: str
    response: str

class VoteOut(BaseModel):
    id: int
    voter_token: str
    response: str
    occurrence_id: int
    created_at: datetime
