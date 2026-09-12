from fastapi import (
    APIRouter,
    Depends
)

from app.middleware.auth_middleware import (
    get_current_user
)

from app.services.database import (
    resumes_collection,
    applications_collection,
    saved_jobs_collection
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def get_dashboard(
    user=Depends(get_current_user)
):

    user_id = user["_id"]

    # ==============================
    # LATEST RESUME
    # ==============================

    latest_resume = (
        resumes_collection
        .find_one(
            {
                "user_id": user_id
            },
            sort=[
                ("created_at", -1)
            ]
        )
    )

    # ==============================
    # APPLICATIONS
    # ==============================

    applications = list(
        applications_collection.find({
            "user_id": user_id
        })
    )

    # ==============================
    # COUNTS
    # ==============================

    application_count = len(
        applications
    )

    interview_count = len([
        application
        for application in applications
        if application.get("status")
        == "Interview"
    ])

    review_count = len([
        application
        for application in applications
        if application.get("status")
        == "Under Review"
    ])

    rejected_count = len([
        application
        for application in applications
        if application.get("status")
        == "Rejected"
    ])

    selected_count = len([
        application
        for application in applications
        if application.get("status")
        == "Selected"
    ])

    saved_jobs_count = (
        saved_jobs_collection.count_documents({
            "user_id": user_id
        })
    )

    # ==============================
    # RESUME DATA
    # ==============================

    resume_score = 0
    ats_score = 0
    job_match = 0
    detected_skills = []
    recommended_skills = []

    if latest_resume:

        analysis = latest_resume.get(
            "analysis",
            {}
        )

        resume_score = analysis.get(
            "resume_score",
            analysis.get(
                "resumeScore",
                0
            )
        )

        ats_score = analysis.get(
            "ats_score",
            analysis.get(
                "atsScore",
                0
            )
        )

        job_match = analysis.get(
            "job_match",
            analysis.get(
                "jobMatch",
                0
            )
        )

        detected_skills = analysis.get(
            "detected_skills",
            analysis.get(
                "detectedSkills",
                []
            )
        )

        recommended_skills = analysis.get(
            "recommended_skills",
            analysis.get(
                "recommendedSkills",
                []
            )
        )

    # ==============================
    # RECENT APPLICATIONS
    # ==============================

    recent_applications = list(
        applications_collection
        .find({
            "user_id": user_id
        })
        .sort(
            "created_at",
            -1
        )
        .limit(5)
    )

    for application in recent_applications:

        application["id"] = str(
            application["_id"]
        )

        del application["_id"]

        if "user_id" in application:
            del application["user_id"]

    # ==============================
    # RESPONSE
    # ==============================

    return {
        "success": True,

        "dashboard": {

            "user": {
                "name": user.get(
                    "name",
                    ""
                ),
                "email": user.get(
                    "email",
                    ""
                )
            },

            "overview": {

                "resume_score":
                    resume_score,

                "ats_score":
                    ats_score,

                "job_match":
                    job_match,

                "applications":
                    application_count,

                "saved_jobs":
                    saved_jobs_count,

                "interviews":
                    interview_count,

                "under_review":
                    review_count,

                "rejected":
                    rejected_count,

                "selected":
                    selected_count
            },

            "skills": {

                "detected":
                    detected_skills,

                "recommended":
                    recommended_skills
            },

            "latest_resume": (
                {
                    "id": str(
                        latest_resume["_id"]
                    ),
                    "original_name":
                        latest_resume.get(
                            "original_name",
                            ""
                        ),
                    "target_role":
                        latest_resume.get(
                            "target_role",
                            ""
                        ),
                    "analysis":
                        latest_resume.get(
                            "analysis",
                            {}
                        )
                }
                if latest_resume
                else None
            ),

            "recent_applications":
                recent_applications
        }
    }