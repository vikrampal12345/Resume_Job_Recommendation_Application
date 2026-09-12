from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.predictor import ResumePredictor
from app.ocr import extract_resume_text
from app.job_api import search_jobs
from app.job_formatter import format_job_name

from app.requirement_extractor import extract_requirements
from app.evidence_engine import analyze_job as analyze_job_evidence
from app.decision_engine import decide_from_job_analysis
from app.resume_relevance_filter import filter_resume_relevance

import shutil
import os
import uuid
import traceback


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Syncronal Career Decision API",
    description="AI-powered resume analysis, job recommendation and evidence-backed job decision engine.",
    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://syncronal.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# INITIALIZE RESUME PREDICTOR
# ============================================================

predictor = ResumePredictor()


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = os.path.join(
    os.path.dirname(__file__),
    "uploads"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Syncronal Career Decision API is running.",
        "version": "2.0.0",
        "endpoints": {
            "predict": "/predict",
            "live_jobs": "/live-jobs",
            "analyze_job": "/analyze-job",
            "debug_origin": "/debug-origin"
        }
    }


# ============================================================
# PREDICT / RESUME ANALYSIS
# ============================================================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    allowed_extensions = [".pdf", ".docx"]

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    unique_filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # -----------------------------------------------
        # STEP 1: Extract text
        # -----------------------------------------------

        resume_text = extract_resume_text(file_path)

        # -----------------------------------------------
        # STEP 2: Resume Relevance Filter
        # -----------------------------------------------

        validation = filter_resume_relevance(resume_text)

        print("\n========== RESUME VALIDATION ==========")
        print("Classification:", validation["classification"])
        print("Score:", validation["score"])
        print("Confidence:", validation["confidence"])
        print("Document Type:", validation["document_type"])
        print("Reason:", validation["reason"])
        print("Continue:", validation["continue_pipeline"])
        print("=======================================\n")

        # -----------------------------------------------
        # STEP 3: STOP if not a resume
        # -----------------------------------------------

        if not validation["continue_pipeline"]:

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_RESUME",
                    "message": (
                        "The uploaded document does not appear "
                        "to be a valid resume or CV. "
                        "Please upload a resume."
                    ),
                    "classification": validation["classification"],
                    "document_type": validation["document_type"],
                    "confidence": validation["confidence"],
                    "score": validation["score"],
                    "reason": validation["reason"],
                }
            )

        # -----------------------------------------------
        # STEP 4: ONLY NOW run AI recommendation
        # -----------------------------------------------

        result = predictor.predict(resume_text)

        return {
            "success": True,
            "validation": validation,
            "recommendations": result.get(
                "recommendations",
                []
            )
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)

    temp_file = None

    try:

        # --------------------------------------------------------
        # Validate file type
        # --------------------------------------------------------

        filename = file.filename or ""

        allowed_extensions = {
            ".pdf",
            ".docx"
        }

        extension = os.path.splitext(filename)[1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX resume files are supported."
            )

        # --------------------------------------------------------
        # Generate temporary filename
        # --------------------------------------------------------

        temp_filename = f"{uuid.uuid4()}{extension}"

        temp_file = os.path.join(
            UPLOAD_DIR,
            temp_filename
        )

        # --------------------------------------------------------
        # Save uploaded file
        # --------------------------------------------------------

        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # --------------------------------------------------------
        # Extract resume text
        # --------------------------------------------------------

        resume_text = extract_resume_text(
            temp_file
        )

        if not resume_text or not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the resume."
            )

        # --------------------------------------------------------
        # Existing resume prediction system
        # --------------------------------------------------------

        result = predictor.predict(
            resume_text
        )

        # --------------------------------------------------------
        # Make sure result is a dictionary
        # --------------------------------------------------------

        if not isinstance(result, dict):
            result = {
                "prediction": result
            }

        # --------------------------------------------------------
        # IMPORTANT:
        # Return resume_text so frontend can reuse it
        # for /analyze-job
        # --------------------------------------------------------

        result["resume_text"] = resume_text

        return result

    except HTTPException:
        raise

    except Exception as e:

        print("\n[PREDICT ERROR]")
        print(str(e))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Resume prediction failed: {str(e)}"
        )

    finally:

        # --------------------------------------------------------
        # Delete temporary uploaded file
        # --------------------------------------------------------

        if temp_file and os.path.exists(temp_file):

            try:
                os.remove(temp_file)

            except Exception as cleanup_error:

                print(
                    "[UPLOAD CLEANUP ERROR]",
                    cleanup_error
                )


# ============================================================
# LIVE JOB SEARCH
# ============================================================

# ============================================================
# LIVE JOB SEARCH
# ============================================================

class LiveJobsRequest(BaseModel):

    target_role: str


@app.post("/live-jobs")
def live_jobs(
    request: LiveJobsRequest
):

    try:

        # --------------------------------------------------------
        # Validate target role
        # --------------------------------------------------------

        target_role = request.target_role.strip()

        if not target_role:

            raise HTTPException(
                status_code=400,
                detail="Target role cannot be empty."
            )

        # --------------------------------------------------------
        # Search jobs ONLY for the role selected/typed by user
        # --------------------------------------------------------

        print("\n[LIVE JOB SEARCH]")
        print(f"Target Role : {target_role}")

        jobs = search_jobs(
            target_role
        )

        # --------------------------------------------------------
        # Format returned job titles
        # --------------------------------------------------------

        all_jobs = []

        for job in jobs:

            try:

                job["job_title"] = format_job_name(
                    job.get(
                        "job_title",
                        ""
                    )
                )

            except Exception:
                pass

            all_jobs.append(job)

        # --------------------------------------------------------
        # Final response
        # --------------------------------------------------------

        return {
            "success": True,
            "target_role": target_role,
            "jobs": all_jobs
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n[LIVE JOB ERROR]")
        print(str(e))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Live job search failed: {str(e)}"
        )
# ============================================================
# JOB ANALYSIS REQUEST
# ============================================================

class JobAnalysisRequest(BaseModel):

    # ========================================================
    # CANDIDATE RESUME
    # ========================================================

    resume_text: str

    # ========================================================
    # JSEARCH JOB DATA
    # ========================================================

    company: str | None = None

    job_title: str | None = None

    location: str | None = None

    employment_type: str | None = None

    salary: str | None = None

    posted_date: str | None = None

    apply_link: str | None = None

    job_description: str

    job_id: str | None = None


# ============================================================
# ANALYZE SPECIFIC JOB
# ============================================================

@app.post("/analyze-job")
def analyze_job_endpoint(
    request: JobAnalysisRequest
):

    try:

        print("\n")
        print("=" * 70)
        print("SYNCRONAL JOB ANALYSIS")
        print("=" * 70)

        print(
            f"Company     : {request.company}"
        )

        print(
            f"Job Title   : {request.job_title}"
        )

        print(
            f"Location    : {request.location}"
        )

        print("=" * 70)

        # ====================================================
        # VALIDATE RESUME
        # ====================================================

        if not request.resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail="resume_text cannot be empty."
            )

        # ====================================================
        # VALIDATE JOB DESCRIPTION
        # ====================================================

        if not request.job_description.strip():

            raise HTTPException(
                status_code=400,
                detail="job_description cannot be empty."
            )

        # ====================================================
        # STEP 1
        # REQUIREMENT EXTRACTION
        # ====================================================

        print(
            "\n[1/3] Extracting job requirements..."
        )

        requirements = extract_requirements(
            request.job_description,
            use_llm=True
        )

        print(
            "[RequirementExtractor] Completed."
        )

        # ====================================================
        # STEP 2
        # EVIDENCE ENGINE
        # ====================================================

        print(
            "\n[2/3] Finding resume evidence..."
        )

        evidence_result = analyze_job_evidence(
            resume_text=request.resume_text,
            job_requirements=requirements
        )

        print(
            "[EvidenceEngine] Completed."
        )

        # ====================================================
        # STEP 3
        # DECISION ENGINE
        # ====================================================

        print(
            "\n[3/3] Making application decision..."
        )

        decision = decide_from_job_analysis(
            evidence_result
        )

        print(
            "[DecisionEngine] Completed."
        )

        print(
            f"\nFINAL DECISION: "
            f"{decision.get('decision')}"
        )

        print("=" * 70)
        print()

        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return {

            "success": True,

            # ------------------------------------------------
            # ORIGINAL JOB
            # ------------------------------------------------

            "job": {

                "company": request.company,

                "job_title": request.job_title,

                "location": request.location,

                "employment_type": request.employment_type,

                "salary": request.salary,

                "posted_date": request.posted_date,

                "apply_link": request.apply_link,

                "job_id": request.job_id
            },

            # ------------------------------------------------
            # EXTRACTED REQUIREMENTS
            # ------------------------------------------------

            "requirements": requirements,

            # ------------------------------------------------
            # RESUME EVIDENCE
            # ------------------------------------------------

            "evidence": evidence_result,

            # ------------------------------------------------
            # FINAL DECISION
            # ------------------------------------------------

            "decision": decision
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n[ANALYZE JOB ERROR]")
        print(str(e))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Job analysis failed: {str(e)}"
        )


# ============================================================
# DEBUG ORIGIN
# ============================================================

@app.get("/debug-origin")
def debug_origin():

    return {
        "success": True,
        "message": "Syncronal backend is reachable.",
        "origin": "FastAPI",
        "version": "2.0.0"
    }