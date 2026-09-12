from datetime import datetime

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
    saved_jobs_collection
)


router = APIRouter(
    prefix="/saved-jobs",
    tags=["Saved Jobs"]
)


class SavedJobRequest(BaseModel):

    job_id: str

    company: Optional[str] = ""
    job_title: Optional[str] = ""

    location: Optional[str] = ""
    employment_type: Optional[str] = ""

    salary: Optional[str] = ""
    apply_link: Optional[str] = ""

    job_description: Optional[str] = ""


def serialize_job(job):

    return {
        "id": str(
            job["_id"]
        ),

        "job_id": job.get(
            "job_id",
            ""
        ),

        "company": job.get(
            "company",
            ""
        ),

        "job_title": job.get(
            "job_title",
            ""
        ),

        "location": job.get(
            "location",
            ""
        ),

        "employment_type": job.get(
            "employment_type",
            ""
        ),

        "salary": job.get(
            "salary",
            ""
        ),

        "apply_link": job.get(
            "apply_link",
            ""
        ),

        "job_description": job.get(
            "job_description",
            ""
        ),

        "created_at": job.get(
            "created_at"
        )
    }


@router.post("/")
def save_job(
    request: SavedJobRequest,
    user=Depends(get_current_user)
):

    existing = saved_jobs_collection.find_one({
        "user_id": user["_id"],
        "job_id": request.job_id
    })

    if existing:

        return {
            "success": True,
            "message": "Job is already saved.",
            "job": serialize_job(
                existing
            )
        }

    job = {
        "user_id": user["_id"],

        "job_id": request.job_id,

        "company": request.company or "",
        "job_title": request.job_title or "",

        "location": request.location or "",
        "employment_type":
            request.employment_type or "",

        "salary": request.salary or "",

        "apply_link":
            request.apply_link or "",

        "job_description":
            request.job_description or "",

        "created_at": datetime.utcnow()
    }

    result = saved_jobs_collection.insert_one(
        job
    )

    job["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Job saved successfully.",
        "job": serialize_job(job)
    }


@router.get("/")
def get_saved_jobs(
    user=Depends(get_current_user)
):

    jobs = list(
        saved_jobs_collection
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
        "jobs": [
            serialize_job(job)
            for job in jobs
        ]
    }


@router.delete("/{job_id}")
def remove_saved_job(
    job_id: str,
    user=Depends(get_current_user)
):

    result = saved_jobs_collection.delete_one({
        "user_id": user["_id"],
        "job_id": job_id
    })

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Saved job not found."
        )

    return {
        "success": True,
        "message": "Job removed from saved jobs."
    }