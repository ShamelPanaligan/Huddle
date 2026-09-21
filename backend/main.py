from fastapi import FastAPI, HTTPException
from db import get_db_connection, init_db, create_user, get_user_by_email, get_user_by_id, add_event_idea, list_event_ideas,get_event_idea, match_event_ideas, list_occurrences_for_idea, create_occurrence, add_vote, get_vote_for_occurrence
from schemas import UserRegister, UserOut, UserLogin, TokenResponse, EventIdeaOut, EventIdeaCreate, MatchRequest,EventOccurrenceOut, EventOccurrenceCreate, VoteOut, VoteCreate
from auth import hash_password, verify_password, create_access_token, decode_access_token
from models import User, EventIdea, EventOccurrence, Vote
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login")

@app.post("/auth/register", response_model = UserOut)
def register(user_in: UserRegister):
    conn = get_db_connection()
    init_db(conn)

    existing = get_user_by_email(conn, user_in.email)
    if existing is not None:
        raise HTTPException(status_code = 400, detail = "Email already registered")

    hashed = hash_password(user_in.password)
    new_user = User(email = user_in.email, password_hash = user_in.password)
    saved_user = create_user(conn, new_user)
    conn.close()
    return saved_user

@app.post("/auth/login", response_model = TokenResponse )
def login(credentials: UserLogin):
    conn = get_db_connection()
    init_db(conn)

    existing = get_user_by_email(conn, credentials.email)
    if existing is None or not verify_password(credentials.password, existing.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    id = existing.id
    token = create_access_token(user_id = id)
    conn.close()
    return TokenResponse(access_token = token, token_type = "bearer")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(status_code = 401, detail = "Invalid or expired token")

    conn = get_db_connection()
    user = get_user_by_id(conn, user_id)

    if user is None:
        raise HTTPException(status_code = 401, detail = "User not found")

    conn.close()
    return user

@app.get("/me", response_model = UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/event-ideas", response_model=EventIdeaOut)
def create_event_idea(idea_in: EventIdeaCreate, current_user: User = Depends(get_current_user)):
    conn = get_db_connection()
    new_idea = EventIdea(creator_id = current_user.id, **idea_in.model_dump())
    saved = add_event_idea(conn, new_idea)
    conn.close()
    return saved

@app.get("/event-ideas", response_model = list[EventIdeaOut])
def get_event_ideas():
    conn = get_db_connection()
    ideas = list_event_ideas(conn)
    conn.close()
    return ideas

@app.get("/event-ideas/{idea_id}", response_model = EventIdeaOut)
def get_event_idea_by_id(idea_id: int):
    conn = get_db_connection()
    event = get_event_ideas(conn, idea_id)
    conn.close()

    if event is None:
        raise HTTPException(status_code=404, detail="No event with this id")

@app.post("/event-ideas/match", response_model= list[EventIdeaOut])
def match_ideas(request: MatchRequest):
    conn = get_db_connection()
    results = match_event_ideas(conn, **request.model_dump())
    conn.close()
    return results

@app.post("/event-ideas/{idea_id}/occurrences", response_model=EventOccurrenceOut)
def create_event_occurrence(idea_id: int, occurrence_in: EventOccurrenceCreate, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    new_occurrence = EventOccurrence(idea_id= idea_id, proposed_time= occurrence_in.proposed_time, created_by= current_user.id)
    saved = create_occurrence(conn, new_occurrence)
    conn.close()
    return saved


@app.get("/event-ideas/{idea_id}/occurrences", response_model= list[EventOccurrenceOut])
def get_occurrence_list(idea_id: int):
    conn = get_db_connection()
    occurrence_list = list_occurrences_for_idea(conn, idea_id)
    conn.close()
    return occurrence_list

@app.post("/occurrences/{occurrence_id}/votes", response_model= VoteOut)
def cast_vote(occurrence_id: int, vote_in: VoteCreate):
    conn = get_db_connection()
    new_vote = Vote(occurrence_id = occurrence_id, voter_token = vote_in.voter_token, response= vote_in.response)
    result = add_vote(conn, new_vote)
    conn.close()

    if result is None: 
        raise HTTPException(status_code=409, detail= "This token has already voted on this occurrence")
    return result

@app.get("/occurrences/{occurrence_id}/votes", response_model=list[VoteOut])
def get_votes(occurrence_id: int):
    conn = get_db_connection()
    vote = get_vote_for_occurrence(conn, occurrence_id)
    conn.close()
    return vote

