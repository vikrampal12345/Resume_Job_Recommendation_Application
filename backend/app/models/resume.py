from datetime import datetime

from app.services.database import resumes_collection


def create_resume_document(
    user_id,
    original_name,
    file_name,
    file_path,
    target_role="",
    job_description="",
    analysis=None
):

    return {
        "user_id": user_id,

        "original_name": original_name,
        "file_name": file_name,
        "file_path": file_path,

        "target_role": target_role,
        "job_description": job_description,

        "analysis": analysis or {},

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def get_user_resumes(user_id):

    return list(
        resumes_collection
        .find(
            {"user_id": user_id},
            {
                "extracted_text": 0
            }
        )
        .sort("created_at", -1)
    )


def get_latest_resume(user_id):

    return resumes_collection.find_one(
        {"user_id": user_id},
        sort=[
            ("created_at", -1)
        ]
    )