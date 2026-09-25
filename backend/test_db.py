import pytest
import sqlite3
from db import init_db

from models import *
from db import *
from datetime import datetime, timedelta


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    init_db(connection)
    yield connection
    connection.close()

def test_create_user_assigns_an_id(conn):
    user = User(email= "person@example.com", password_hash="fake_hash")
    saved = create_user(conn, user)
    assert saved.id is not None

def test_get_user_by_email_found(conn):
    user = User(email= "person@example.com", password_hash="fake_hash")
    saved = create_user(conn, user)
    found_user = get_user_by_email(conn, email = "person@example.com")
    assert found_user is not None
    assert found_user.email == "person@example.com"
    assert found_user.id == saved.id

def test_get_user_by_email_missing_returns_none(conn):
    missing_user = get_user_by_email(conn, email = "fake@mail.com")
    assert missing_user is None

def test_get_user_by_id_found(conn):
    user = User(email= "person@example.com", password_hash="fake_hash")
    saved = create_user(conn,user)
    found_user = get_user_by_id(conn, user_id=saved.id)
    assert found_user is not None
    assert found_user.email == "person@example.com"
    assert found_user.id == saved.id

def test_get_user_by_id_missing_returns_none(conn):
    missing_user = get_user_by_id(conn, user_id= 0)
    assert missing_user is None

def test_duplicate_email_raises_integrity_error(conn):
    user1 = User(email="dupe@example.com", password_hash="fake_hash")
    create_user(conn, user1)

    user2 = User(email="dupe@example.com", password_hash="another_hash")
    with pytest.raises(sqlite3.IntegrityError):
        create_user(conn, user2)

def test_add_event_idea_assigns_an_id(conn):
    owner = create_user(conn, User(email = "myMail@example.com", password_hash= "fake_hash" ))
    new_event = EventIdea(creator_id= owner.id, title= "Dinner", min_headcount=2, max_headcount= 10, duration_min=120, description="Late night at Ivy Asia", budget_pp= "50.00", extra_details="N/A")
    saved = add_event_idea(conn, new_event)
    assert saved.id is not None
    assert saved.title == "Dinner"

def test_add_event_idea_allows_missing_optional_fields(conn):
    owner = create_user(conn, User(email = "myMail@example.com", password_hash= "fake_hash" ))
    new_event = EventIdea(creator_id= owner.id, title= "Climbing", min_headcount=2, max_headcount= 15, duration_min=120)
    saved = add_event_idea(conn, new_event)
    assert saved.id is not None
    assert saved.title == "Climbing"
    assert saved.description is None
    assert saved.budget_pp is None
    assert saved.extra_details is None 

def test_add_event_idea_bad_creator_id_raises_integrity_error(conn):
    bad_event = EventIdea(creator_id= 9999, title= "ExampleTitle", min_headcount=3, max_headcount=7, duration_min=60)
    with pytest.raises(sqlite3.IntegrityError):
        add_event_idea(conn, bad_event)

def test_get_event_idea_found(conn):
    owner = create_user(conn, User(email = "myMail@example.com", password_hash= "fake_hash" ))
    new_event = EventIdea(creator_id= owner.id, title= "Climbing", min_headcount=2, max_headcount= 15, duration_min=120)
    saved = add_event_idea(conn, new_event)
    event_idea = get_event_idea(conn, saved.id)
    assert event_idea is not None


def test_event_idea_missing_returns_none(conn):
    event_idea = get_event_idea(conn, 0)
    assert event_idea is None

def test_list_event_ideas_empty(conn):
    event_list = list_event_ideas(conn)
    assert event_list == []

def test_list_event_ideas_returns_all(conn):
    owner = create_user(conn, User(email = "Fake@mail.com", password_hash= "FakeHash"))
    one_event = EventIdea(creator_id= owner.id, title= "Climbing", min_headcount=2, max_headcount= 15, duration_min=120)
    two_event = EventIdea(creator_id= owner.id, title= "Walking", min_headcount=2, max_headcount= 20, duration_min=360)
    saved_event_one = add_event_idea(conn, one_event)
    saved_event_two = add_event_idea(conn, two_event)
    event_list = list_event_ideas(conn)
    assert len(event_list) == 2
    assert saved_event_one in event_list
    assert saved_event_two in event_list

def test_match_headcount_within_range(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    matching_idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Shopping",
        min_headcount = 5,
        max_headcount= 7,
        duration_min=120))
    non_matching_idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Walk",
        min_headcount = 8,
        max_headcount= 12,
        duration_min=120))
    results = match_event_ideas(conn, headcount=5, available_min=120, budget_cap=None)
    print(results)
    assert matching_idea in results
    assert non_matching_idea not in results   

def test_match_duration_too_long_excluded(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    matching_idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Shopping",
        min_headcount = 5,
        max_headcount= 7,
        duration_min=120))
    non_matching_idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Walk",
        min_headcount = 8,
        max_headcount= 12,
        duration_min=320))
    results = match_event_ideas(conn, headcount=5, available_min=120, budget_cap=None)
    print(results)
    assert matching_idea in results
    assert non_matching_idea not in results   

def test_match_excludes_expensive_prices(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    matching_idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Shopping",
        min_headcount = 5,
        max_headcount= 7,
        duration_min=120,
        budget_pp=30))
    non_matching_idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Dinner",
        min_headcount = 8,
        max_headcount= 12,
        duration_min=120,
        budget_pp= 100))
    results = match_event_ideas(conn, headcount=5, available_min=120, budget_cap=75)
    print(results)
    assert matching_idea in results
    assert non_matching_idea not in results   

def test_create_occurrences_assigns_an_id(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Shopping",
        min_headcount = 5,
        max_headcount= 7,
        duration_min=120,
        budget_pp=30))

    occurrence = create_occurrence(conn, occurrence=EventOccurrence(
        idea_id= idea.id,
        proposed_time=datetime.now() + timedelta(days=3),
        created_by= owner.id
    ))
    assert occurrence.id is not None

def test_create_occurrence_bad_idea_id_raises_integrity_error(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    with pytest.raises(sqlite3.IntegrityError):
        bad_occurrence = create_occurrence(conn, EventOccurrence(
        idea_id= 9999,
        proposed_time=datetime.now() + timedelta(days=3),
        created_by= owner.id
    ))

def test_add_votes_succeed(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Shopping",
        min_headcount = 5,
        max_headcount= 7,
        duration_min=120,
        budget_pp=30))

    occurrence = create_occurrence(conn, occurrence=EventOccurrence(
        idea_id= idea.id,
        proposed_time=datetime.now() + timedelta(days=3),
        created_by= owner.id
    ))

    vote_example = Vote(occurrence_id= occurrence.id, voter_token= "abc123", response="yes")
    saved_vote = add_vote(conn, vote_example)
    assert saved_vote is not None
    assert saved_vote.id is not None
    assert saved_vote.response == "yes"

def test_add_vote_duplicate_token_returns_none(conn):
    owner = create_user(conn, User(email="Fake@mail.com", password_hash="FakeHash"))
    idea = add_event_idea(conn, EventIdea(
        creator_id = owner.id,
        title = "Shopping",
        min_headcount = 5,
        max_headcount= 7,
        duration_min=120,
        budget_pp=30))

    occurrence = create_occurrence(conn, occurrence=EventOccurrence(
        idea_id= idea.id,
        proposed_time=datetime.now() + timedelta(days=3),
        created_by= owner.id
    ))
    
    vote_one = Vote(occurrence_id= occurrence.id, voter_token= "abc123", response="yes")
    vote_two = Vote(occurrence_id= occurrence.id, voter_token= "abc123", response="no")

    first_result = add_vote(conn, vote_one)
    second_result = add_vote(conn, vote_two)

    assert first_result is not None
    assert second_result is None