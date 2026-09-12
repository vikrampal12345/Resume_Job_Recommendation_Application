from datetime import datetime

from bson import ObjectId

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from pydantic import BaseModel

from typing import Optional

from app.middleware.auth_middleware import (
    get_current_user
)

from app.services.database import (
    applications_collection
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


class ApplicationCreate(BaseModel):

    company: str
    job_title: str

    status: str = "Applied"

    job_url: Optional[str] = ""
    location: Optional[str] = ""
    salary: Optional[str] = ""


class ApplicationUpdate(BaseModel):

    status: str


VALID_STATUSES = [
    "Applied",
    "Under Review",
    "Interview",
    "Rejected",
    "Selected"
]


def serialize_application(application):

    return {
        "id": str(
            application["_id"]
        ),

        "company": application.get(
            "company",
            ""
        ),

        "job_title": application.get(
            "job_title",
            ""
        ),

        "status": application.get(
            "status",
            "Applied"
        ),

        "job_url": application.get(
            "job_url",
            ""
        ),

        "location": application.get(
            "location",
            ""
        ),

        "salary": application.get(
            "salary",
            ""
        ),

        "created_at": application.get(
            "created_at"
        )
    }


@router.post("/")
def create_application(
    request: ApplicationCreate,
    user=Depends(get_current_user)
):

    if request.status not in VALID_STATUSES:

        raise HTTPException(
            status_code=400,
            detail="Invalid application status."
        )

    document = {
        "user_id": user["_id"],

        "company": request.company,
        "job_title": request.job_title,

        "status": request.status,

        "job_url": request.job_url or "",
        "location": request.location or "",
        "salary": request.salary or "",

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = applications_collection.insert_one(
        document
    )

    document["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Application added successfully.",
        "application": serialize_application(
            document
        )
    }


@router.get("/")
def get_applications(
    user=Depends(get_current_user)
):

    applications = list(
        applications_collection
        .find({
            "user_id": user["_id"]
        })
        .sort(
            "created_at",
            -1
        )
    )

    return {
        "success": True,
        "applications": [
            serialize_application(
                application
            )
            for application in applications
        ]
    }


@router.put("/{application_id}")
def update_application(
    application_id: str,
    request: ApplicationUpdate,
    user=Depends(get_current_user)
):

    if request.status not in VALID_STATUSES:

        raise HTTPException(
            status_code=400,
            detail="Invalid application status."
        )

    try:

        object_id = ObjectId(
            application_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid application ID."
        )

    result = applications_collection.update_one(
        {
            "_id": object_id,
            "user_id": user["_id"]
        },

        {
            "$set": {
                "status": request.status,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    application = applications_collection.find_one({
        "_id": object_id
    })

    return {
        "success": True,
        "message": "Application updated successfully.",
        "application": serialize_application(
            application
        )
    }


@router.delete("/{application_id}")
def delete_application(
    application_id: str,
    user=Depends(get_current_user)
):

    try:

        object_id = ObjectId(
            application_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid application ID."
        )

    result = applications_collection.delete_one({
        "_id": object_id,
        "user_id": user["_id"]
    })

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    return {
        "success": True,
        "message": "Application deleted successfully."
    }