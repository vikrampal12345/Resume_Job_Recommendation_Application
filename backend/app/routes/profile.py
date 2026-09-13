from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.middleware.auth_middleware import get_current_user
from app.services.database import users_collection


# =========================================
# ROUTER
# =========================================

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


# =========================================
# PROFILE UPDATE MODEL
# =========================================

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    role: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None


# =========================================
# SERIALIZE USER
# =========================================

def serialize_user(user):
    """
    Convert MongoDB user document into
    JSON-safe profile data.
    """

    if not user:
        return None

    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "location": user.get("location", ""),
        "role": user.get("role", ""),
        "education": user.get("education", ""),
        "experience": user.get("experience", "Fresher"),
        "bio": user.get("bio", ""),
        "skills": user.get("skills", []),
    }


# =========================================
# GET PROFILE
# =========================================

@router.get("/")
def get_profile(
    user=Depends(get_current_user)
):
    """
    Get profile of the currently
    authenticated user.
    """

    return {
        "success": True,
        "user": serialize_user(user),
    }


# =========================================
# UPDATE PROFILE
# =========================================

@router.put("/")
def update_profile(
    request: ProfileUpdate,
    user=Depends(get_current_user)
):
    """
    Update profile of the currently
    authenticated user.

    The data is stored permanently
    in MongoDB.
    """

    update_data = {}

    # -------------------------------------
    # Fields that can be updated
    # -------------------------------------

    fields = [
        "name",
        "phone",
        "location",
        "role",
        "education",
        "experience",
        "bio",
        "skills",
    ]

    # -------------------------------------
    # Get values from request
    # -------------------------------------

    for field in fields:

        value = getattr(request, field)

        if value is not None:

            # Remove unnecessary spaces
            # from text fields
            if isinstance(value, str):
                value = value.strip()

            update_data[field] = value

    # -------------------------------------
    # Updated timestamp
    # -------------------------------------

    update_data["updated_at"] = datetime.now(
        timezone.utc
    )

    # -------------------------------------
    # Update CURRENT USER in MongoDB
    #
    # IMPORTANT:
    # user["_id"] comes from JWT
    # authenticated user.
    # -------------------------------------

    result = users_collection.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": update_data
        }
    )

    # -------------------------------------
    # Check whether user was found
    # -------------------------------------

    if result.matched_count == 0:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    # -------------------------------------
    # Get updated user
    # -------------------------------------

    updated_user = users_collection.find_one(
        {
            "_id": user["_id"]
        }
    )

    if not updated_user:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Unable to retrieve updated profile."
        )

    # -------------------------------------
    # Return updated data
    # -------------------------------------

    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": serialize_user(updated_user),
    }