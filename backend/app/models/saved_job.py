from datetime import datetime

from app.services.database import saved_jobs_collection


def create_saved_job_document(
    user_id,
    job
):

    return {
        "user_id": user_id,

        "job_id": str(
            job.get("job_id")
            or job.get("id")
            or ""
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

        "created_at": datetime.utcnow()
    }