from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    email: str 
    password_hash: str
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class EventIdea:
    creator_id: int
    title: str
    min_headcount: int
    max_headcount: int
    duration_min: int
    id: int | None = None
    description: str | None = None
    budget_pp: float | None = None
    extra_details: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class EventOccurrence:
    idea_id: int
    proposed_time: datetime
    created_by: int
    id: int |  None = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Vote:
    occurrence_id: int
    voter_token: str
    response: str
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)

