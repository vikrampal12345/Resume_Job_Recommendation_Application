from bson import ObjectId

from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from app.services.auth_service import (
    decode_access_token
)

from app.services.database import (
    users_collection
)


# =========================================
# HTTP BEARER SECURITY
# =========================================

security = HTTPBearer()


# =========================================
# GET CURRENT USER
# =========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):
    """
    Get the currently authenticated user
    from the JWT token.

    Flow:

    Frontend
        ↓
    Authorization: Bearer <token>
        ↓
    Decode JWT
        ↓
    Get user ID from 'sub'
        ↓
    Find user in MongoDB
        ↓
    Return user document
    """

    # -------------------------------------
    # Get token from Authorization header
    # -------------------------------------

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is missing."
        )

    # -------------------------------------
    # Decode and verify JWT
    # -------------------------------------

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # -------------------------------------
    # Get user ID
    #
    # auth_service.py stores it as:
    #
    # "sub": str(user_id)
    # -------------------------------------

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    # -------------------------------------
    # Convert string ID to MongoDB ObjectId
    # -------------------------------------

    try:

        object_id = ObjectId(user_id)

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid user ID."
        )

    # -------------------------------------
    # Find user in MongoDB
    # -------------------------------------

    user = users_collection.find_one(
        {
            "_id": object_id
        }
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    # -------------------------------------
    # Return complete MongoDB user document
    # -------------------------------------

    return user