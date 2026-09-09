from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config import JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

JWT_ALGORIITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.now() +timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = {
        "sub": str(user_id),
        "exp": expire,
    }
    token = jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORIITHM)
    return token

def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY , algorithms=[JWT_ALGORIITHM])
        user_id = payload['sub']
        return int(user_id)
    except JWTError:
        return None
