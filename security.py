from passlib.context import CryptContext
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "G35sVco7B9r$AkQI5@zU073K6W!0JVqMVE8KGpuS3I5x53S&cq94Vdw7fm$SnNpj5Kl!QgD60cEGx!!cm1*m83q5jjEvED^a5%ixXkSmm2Z8MWCUwManw@cfWh5^8o"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login/")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except PyJWTError:
        return None

async def get_current_user(token: str = Security(oauth2_scheme)) -> int:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token corrupto")
