"""
FastAPI dependencies for authentication and authorization.

CRITICAL SECURITY: This module validates JWT tokens and extracts user_id.
ALL protected endpoints MUST use get_current_user_id dependency.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import settings


security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validates JWT token and extracts user_id.

    CRITICAL: All protected endpoints must use this dependency to ensure:
    1. User is authenticated (valid JWT)
    2. User identity is extracted for data filtering

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        user_id: String identifier from JWT 'sub' claim

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing user_id

    Usage:
        @app.get("/api/tasks")
        async def get_tasks(user_id: str = Depends(get_current_user_id)):
            # user_id is now available and verified
            tasks = await session.exec(
                select(Task).where(Task.user_id == user_id)
            )
    """
    token = credentials.credentials

    try:
        # Decode JWT using shared secret
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )

        # Extract user_id from 'sub' claim (Better Auth standard)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
