from datetime import datetime, timezone
from typing import Any, Dict

from app.database import (
    get_resume_analyses_collection,
    get_applications_collection,
)


# =========================================================
# RESUME ANALYSIS HISTORY
# =========================================================

def save_analysis_history(
    user_id: str,
    resume_name: str,
    analysis_result: Dict[str, Any],
) -> str:
    """
    Save one resume analysis record into MongoDB.
    """

    document = {
        "user_id": user_id,
        "resume_name": resume_name,
        "analyzed_at": datetime.now(timezone.utc),
        "analysis_result": analysis_result,
    }

    collection = get_resume_analyses_collection()

    result = collection.insert_one(document)

    return str(result.inserted_id)


# =========================================================
# APPLICATION HISTORY
# =========================================================

def save_application_history(
    user_id: str,
    job_id: str,
    company: str,
    job_title: str,
    apply_link: str,
    status: str = "APPLIED",
    source: str = "JSearch",
) -> str:
    """
    Save one applied-job record into MongoDB.
    """

    document = {
        "user_id": user_id,
        "job_id": job_id,
        "company": company,
        "job_title": job_title,
        "apply_link": apply_link,
        "applied_at": datetime.now(timezone.utc),
        "status": status,
        "source": source,
    }

    collection = get_applications_collection()

    result = collection.insert_one(document)

    return str(result.inserted_id)


# =========================================================
# GET RESUME ANALYSIS HISTORY
# =========================================================

def get_analysis_history(
    user_id: str,
) -> list[Dict[str, Any]]:
    """
    Get all resume analysis records for one user.
    """

    collection = get_resume_analyses_collection()

    records = collection.find(
        {
            "user_id": user_id
        }
    ).sort(
        "analyzed_at",
        -1
    )

    history = []

    for record in records:
        record["_id"] = str(record["_id"])
        history.append(record)

    return history


# =========================================================
# GET APPLICATION HISTORY
# =========================================================

def get_application_history(
    user_id: str,
) -> list[Dict[str, Any]]:
    """
    Get all application records for one user.
    """

    collection = get_applications_collection()

    records = collection.find(
        {
            "user_id": user_id
        }
    ).sort(
        "applied_at",
        -1
    )

    history = []

    for record in records:
        record["_id"] = str(record["_id"])
        history.append(record)

    return history