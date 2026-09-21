import pytest
import sqlite3
from db import init_db

from models import User
from db import create_user, get_user_by_email, get_user_by_id

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