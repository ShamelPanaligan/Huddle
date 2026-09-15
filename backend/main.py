from fastapi import FastAPI, HTTPException
from db import get_db_connection, init_db, create_user, get_user_by_email
from schemas import UserRegister, UserOut, UserLogin, TokenResponse
from auth import hash_password, verify_password, create_access_token 
from models import User

app = FastAPI()

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

