from datetime import datetime

from app.services.database import applications_collection


VALID_STATUSES = [
    "Applied",
    "Under Review",
    "Interview",
    "Rejected",
    "Selected"
]


def create_application_document(
    user_id,
    company,
    job_title,
    status="Applied",
    job_url="",
    location="",
    salary=""
):

    if status not in VALID_STATUSES:
        status = "Applied"

    return {
        "user_id": user_id,

        "company": company,
        "job_title": job_title,

        "status": status,

        "job_url": job_url,
        "location": location,
        "salary": salary,

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }