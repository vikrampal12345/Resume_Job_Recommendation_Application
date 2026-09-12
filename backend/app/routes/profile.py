from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from app.middleware.auth_middleware import (
    get_current_user
)

from app.services.database import (
    users_collection
)


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


class ProfileUpdate(BaseModel):

    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    role: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None


def serialize_user(user):

    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "location": user.get("location", ""),
        "role": user.get("role", ""),
        "education": user.get("education", ""),
        "experience": user.get(
            "experience",
            "Fresher"
        ),
        "bio": user.get("bio", ""),
        "skills": user.get(
            "skills",
            []
        )
    }


@router.get("/")
def get_profile(
    user=Depends(get_current_user)
):

    return {
        "success": True,
        "user": serialize_user(user)
    }


@router.put("/")
def update_profile(
    request: ProfileUpdate,
    user=Depends(get_current_user)
):

    update_data = {}

    fields = [
        "name",
        "phone",
        "location",
        "role",
        "education",
        "experience",
        "bio",
        "skills"
    ]

    for field in fields:

        value = getattr(
            request,
            field
        )

        if value is not None:

            update_data[field] = value

    from datetime import datetime

    update_data["updated_at"] = (
        datetime.utcnow()
    )

    users_collection.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": update_data
        }
    )

    updated_user = users_collection.find_one({
        "_id": user["_id"]
    })

    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": serialize_user(
            updated_user
        )
    }