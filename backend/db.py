import sqlite3
from datetime import datetime
from pathlib import Path
from models import User, EventIdea, EventOccurrence, Vote

DB_PATH = Path.home() / "event_matcher.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL) """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS eventIdeas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT,
    min_headcount INTEGER NOT NULL,
    max_headcount INTEGER NOT NULL,
    duration_min INTEGER NOT NULL,
    budget_pp REAL,
    extra_details TEXT,
    created_at TEXT NOT NULL

    )""")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS eventOccurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL REFERENCES eventIdeas(id),
    proposed_time TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id) NOT NULL,
    created_at TEXT NOT NULL

    )""")

    conn.execute("""

    CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurrence_id INTEGER NOT NULL REFERENCES eventOccurrences(id),
    voter_token TEXT NOT NULL,  
    response TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(occurrence_id, voter_token)
    )""")

    conn.commit()

def create_user(conn : sqlite3.Connection, user: User) -> User:
    cursor = conn.execute("""
    INSERT INTO users (email, password_hash, created_at) 
    VALUES (?, ?, ?)""",
    (user.email,user.password_hash, user.created_at.isoformat())
    )
    conn.commit()
    user.id = cursor.lastrowid
    return user

def add_event_idea(conn: sqlite3.Connection, event_idea: EventIdea) -> EventIdea:
    cursor = conn.execute("""
    INSERT INTO eventIdeas (creator_id, title, min_headcount, max_headcount, duration_min,
    description, budget_pp, extra_details, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (event_idea.creator_id, event_idea.title, event_idea.min_headcount, event_idea.max_headcount,
    event_idea.duration_min, event_idea.description, event_idea.budget_pp, event_idea.extra_details, event_idea.created_at.isoformat())
    )
    conn.commit()
    event_idea.id = cursor.lastrowid
    return event_idea
    

def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id = row["id"],
        email = row["email"],
        password_hash = row["password_hash"],
        created_at= datetime.fromisoformat(row["created_at"])
    )

def _row_to_eventIdea(row:sqlite3.Row) -> EventIdea:
    return EventIdea(
        creator_id = row["creator_id"],
        title = row["title"],
        min_headcount = row["min_headcount"],
        max_headcount = row["max_headcount"],
        duration_min= row["duration_min"],
        id = row["id"],
        description = row["description"],
        budget_pp = row["budget_pp"],
        extra_details = row["extra_details"],
        created_at = row["created_at"]
    )

def get_user_by_email(conn: sqlite3.Connection, email: str) -> User | None:
    row = conn.execute("SELECT * FROM users WHERE email = ? ", (email,)).fetchone()
    return  _row_to_user(row) if row else None

def get_event_idea(conn: sqlite3.Connection, idea_id: int) -> EventIdea | None:
    row = conn.execute("SELECT * FROM eventIdeas WHERE id = ? ", (idea_id,)).fetchone()
    return _row_to_eventIdea(row) if row else None

def list_event_ideas(conn: sqlite3.Connection) -> list[EventIdea]:
    rows = conn.execute("SELECT * FROM eventIdeas ORDER BY created_at DESC").fetchall()
    return [_row_to_eventIdea(row) for row in rows]

def match_event_ideas(conn: sqlite3.Connection, headcount: int, available_min: int, budget_cap: float | None = None) -> list[EventIdea]:
    rows = conn.execute("""
    SELECT * FROM eventIdeas
    WHERE min_headcount <= ?
    AND max_headcount >= ?
    AND duration_min <= ?
    AND (budget_pp IS NULL OR budget_pp <= ?)
    ORDER BY created_at DESC    
    """, (headcount, headcount ,available_min, budget_cap),).fetchall()
    return [_row_to_eventIdea(row) for row in rows]

def create_occurrence(conn: sqlite3.Connection, occurrence: EventOccurrence) -> EventOccurrence:
    cursor = conn.execute("""
    INSERT into eventOccurrences (idea_id, proposed_time, created_by, created_at)
    VALUES (?, ?, ?, ?)
    """, (occurrence.idea_id, occurrence.proposed_time.isoformat(), occurrence.created_by, occurrence.created_at.isoformat()))
    occurrence.id = cursor.lastrowid
    conn.commit()
    return occurrence

def _row_to_eventOccurence(row: sqlite3.Row) -> EventOccurrence:
    return EventOccurrence(
        idea_id = row["idea_id"],
        proposed_time = datetime.fromisoformat(row["proposed_time"]),
        created_by = row["created_by"],
        id = row["id"],
        created_at = datetime.fromisoformat(row["created_at"])
    )
    

def list_occurrences_for_idea(conn: sqlite3.Connection, idea_id: int) -> list[EventOccurrence]:
    rows = conn.execute("SELECT * FROM eventOccurrences WHERE idea_id = ? ORDER BY created_at DESC", (idea_id,)).fetchall()
    return [ _row_to_eventOccurence(row) for row in rows]

def add_vote(conn: sqlite3.Connection, vote: Vote) -> Vote:
    try:
        cursor = conn.execute("""
        INSERT INTO votes (occurrence_id, voter_token, response, created_at)
        VALUES (?, ?, ?, ?) 
        """, (vote.occurrence_id, vote.voter_token, vote.response, vote.created_at.isoformat()))
        vote.id = cursor.lastrowid
        conn.commit()
        return vote
    except sqlite3.IntegrityError:
        return None
    
def _row_to_vote(row: sqlite3.Row) -> Vote:
    return Vote(
        occurrence_id = row["occurrence_id"],
        voter_token = row["voter_token"],
        response = row["response"],
        id = row["id"],
        created_at = datetime.fromisoformat(row["created_at"])
    )

def get_vote_for_occurrence(conn: sqlite3.Connection, occurence_id: int) -> list[Vote]:
    rows = conn.execute("SELECT * FROM votes WHERE occurrence_id = ? ORDER BY created_at DESC", (occurence_id,)).fetchall()
    return [_row_to_vote(row) for row in rows]
