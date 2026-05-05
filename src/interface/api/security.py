import time
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.infrastructure.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

# This defines the FastAPI security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": time.time() + 3600}) # 1 hour expiration
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    """RBAC Guardrail: Verifies the JWT token from the request."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
