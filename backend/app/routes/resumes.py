from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import (
    get_current_user
)

from app.models.resume import (
    get_user_resumes,
    get_latest_resume
)


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


def serialize_resume(resume):

    return {
        "id": str(
            resume["_id"]
        ),

        "original_name": resume.get(
            "original_name",
            ""
        ),

        "file_name": resume.get(
            "file_name",
            ""
        ),

        "target_role": resume.get(
            "target_role",
            ""
        ),

        "job_description": resume.get(
            "job_description",
            ""
        ),

        "analysis": resume.get(
            "analysis",
            {}
        ),

        "created_at": resume.get(
            "created_at"
        )
    }


@router.get("/")
def get_resumes(
    user=Depends(get_current_user)
):

    resumes = get_user_resumes(
        user["_id"]
    )

    return {
        "success": True,
        "resumes": [
            serialize_resume(
                resume
            )
            for resume in resumes
        ]
    }


@router.get("/latest")
def get_latest(
    user=Depends(get_current_user)
):

    resume = get_latest_resume(
        user["_id"]
    )

    if not resume:

        return {
            "success": True,
            "resume": None
        }

    return {
        "success": True,
        "resume": serialize_resume(
            resume
        )
    }