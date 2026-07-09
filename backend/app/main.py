from fastapi import FastAPI, UploadFile, File, HTTPException
from app.predictor import ResumePredictor
from app.ocr import extract_resume_text
import shutil
import os
import uuid
import traceback
# ===========================================
# FastAPI App
# ===========================================

app = FastAPI(
    title="Resume Recommendation API",
    version="1.0.0"
)

# ===========================================
# Load Predictor Once
# ===========================================

predictor = ResumePredictor()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# ===========================================
# Request Model
# ===========================================

# class ResumeRequest(BaseModel):
#     resume_text: str

# ===========================================
# Home Route
# ===========================================

@app.get("/")
def home():
    return {
        "message": "Resume Recommendation API Running Successfully"
    }

# ===========================================
# Prediction Route
# ===========================================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Allowed extensions
    allowed_extensions = [".pdf", ".docx"]

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    # Unique filename
    unique_filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # OCR
        resume_text = extract_resume_text(file_path)

        # Recommendation
        result = predictor.predict(resume_text)

        return result

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)