import os
import cv2
import easyocr
import pandas as pd
from tqdm import tqdm

# ==========================
# Initialize EasyOCR
# ==========================

reader = easyocr.Reader(
    ['en'],
    gpu=True
)

# ==========================
# Dataset Path
# ==========================

DATASET_PATH = "Resumes Datasets"

# ==========================
# Output CSV
# ==========================

OUTPUT_CSV = "data/extracted/resume_text.csv"

# ==========================
# Image Extensions
# ==========================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png"
)

# ==========================
# Collect Images
# ==========================

image_paths = []

for root, dirs, files in os.walk(DATASET_PATH):

    for file in files:

        if file.lower().endswith(IMAGE_EXTENSIONS):

            image_paths.append(
                os.path.join(root, file)
            )

print(f"Total Images Found : {len(image_paths)}")

image_paths = image_paths[:100]

print(f"Processing {len(image_paths)} images...")

sample_image = image_paths[0]

result = reader.readtext(
    sample_image,
    detail=0,
    paragraph=True
)

text = " ".join(result)

print(text)