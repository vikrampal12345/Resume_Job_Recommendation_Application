from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import (
    decode_access_token
)

from app.services.database import (
    users_collection
)


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    try:

        payload = decode_access_token(
            token
        )

        user_id = payload.get(
            "user_id"
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token."
            )

        try:
            object_id = ObjectId(
                user_id
            )
        except Exception:

            raise HTTPException(
                status_code=401,
                detail="Invalid user ID."
            )

        user = users_collection.find_one({
            "_id": object_id
        })

        if not user:

            raise HTTPException(
                status_code=401,
                detail="User not found."
            )

        return user

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )