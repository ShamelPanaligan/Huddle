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

    CREATE TABLE IF NOT EXISTS Vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurrence_id INTEGER NOT NULL REFERENCES eventOccurrences(id),
    voter_token TEXT NOT NULL,  
    response TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(occurrence_id, voter_token)
    )""")

    conn.commit()