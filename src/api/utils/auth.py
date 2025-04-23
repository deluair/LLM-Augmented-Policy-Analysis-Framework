"""
API Authentication Utilities.

Handles tasks like API key validation, token verification, etc.
"""

import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# Placeholder for future JWT validation if needed
# from jose import JWTError, jwt
# from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# --- Configuration --- 
# In a real app, load these from environment variables or a config file
API_KEY = os.environ.get("POLICY_ANALYSIS_API_KEY", "default_insecure_key") # Example: Load from env var
API_KEY_NAME = "X-API-KEY" # Standard header name for API keys

# Placeholder JWT settings (if using JWT)
# SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "a_very_secret_key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- API Key Authentication --- 

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_api_key(api_key_header: str = Depends(api_key_header_auth)) -> bool:
    """Validates the API key provided in the request header.

    Args:
        api_key_header (str): The API key extracted from the header by FastAPI.

    Raises:
        HTTPException: If the API key is invalid.

    Returns:
        bool: True if the API key is valid.
    """
    if api_key_header == API_KEY:
        logger.debug(f"Valid API Key received ending in '...{api_key_header[-4:]}'") # Log last 4 chars for verification
        return True
    else:
        logger.warning(f"Invalid API Key received ending in '...{api_key_header[-4:]}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "API Key"}, # Correct header might vary
        )

# --- JWT Authentication (Placeholder) --- 

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # If using OAuth2 for token endpoint

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         # Here you would typically load the user from DB based on username
#         # For now, just return the username
#         return {"username": username}
#     except JWTError:
#         raise credentials_exception

# --- Simple Dependency for API Key Validation --- 

# This can be used in FastAPI route definitions like: `Depends(get_api_key)`
async def get_api_key(api_key: bool = Depends(validate_api_key)):
    """FastAPI dependency that simply runs the API key validation."""
    # The actual validation happens in `validate_api_key`
    # This function primarily exists to be used cleanly in `Depends()`
    if not api_key: # Should not happen due to auto_error=True, but for safety
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    # Can return the key or True, or nothing if just used for the side effect of validation
    return True 

logger.info("API Authentication utilities loaded.")

# Example Usage in a FastAPI route:
# from fastapi import FastAPI, Depends
# from .auth import get_api_key
# 
# app = FastAPI()
# 
# @app.get("/secure-data")
# async def get_secure_data(api_key: bool = Depends(get_api_key)):
#     # If code reaches here, API key is valid
#     return {"message": "This is secure data."}
