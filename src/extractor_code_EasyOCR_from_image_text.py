import os
import re
import easyocr
import pandas as pd
from tqdm import tqdm

# ==========================================
# Initialize EasyOCR
# ==========================================

reader = easyocr.Reader(['en'], gpu=True)

# ==========================================
# Dataset Path
# ==========================================

DATASET_PATH = "Resumes Datasets"

# ==========================================
# Output Folder
# ==========================================

OUTPUT_FOLDER = "data/extracted"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "resume_text_8500_9063.csv")

# ==========================================
# Supported Image Extensions
# ==========================================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png"
)

# ==========================================
# Collect All Images
# ==========================================

image_paths = []

for root, dirs, files in os.walk(DATASET_PATH):

    for file in files:

        if file.lower().endswith(IMAGE_EXTENSIONS):

            image_paths.append(
                os.path.join(root, file)
            )

print(f"\nTotal Images Found : {len(image_paths)}")

# ==========================================
# Process Only First you want images Images
# ==========================================

image_paths = image_paths[8500:9063]

print(f"Processing {len(image_paths)} Images...\n")

# ==========================================
# Text Cleaning Function
# ==========================================

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    return text.strip()

# ==========================================
# OCR Extraction
# ==========================================

data = []

for image_path in tqdm(image_paths, desc="Extracting Resumes"):

    try:

        result = reader.readtext(
            image_path,
            detail=0,
            paragraph=True
        )

        text = " ".join(result)

        text = clean_text(text)

        data.append({

            "filename": os.path.basename(image_path),

            "file_path": image_path,

            "resume_text": text

        })

    except Exception as e:

        print(f"\nError Processing : {image_path}")

        print(e)

# ==========================================
# Create DataFrame
# ==========================================

df = pd.DataFrame(data)

print("\nDataFrame Shape :", df.shape)

print(df.head())

# ==========================================
# Save CSV
# ==========================================

df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print("\n====================================")
print("CSV Saved Successfully!")
print("Location :", OUTPUT_CSV)
print("====================================")