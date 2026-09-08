from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config import JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

JWT_ALGORIITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60