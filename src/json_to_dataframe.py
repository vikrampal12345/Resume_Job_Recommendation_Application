import os
import json
import pandas as pd
from tqdm import tqdm

# ==========================================
# Paths
# ==========================================

INPUT_CSV = "data/extracted/clean_resume.csv"
JSON_FOLDER = "data/annotations"
OUTPUT_CSV = "data/annotated/annotated_resume.csv"

os.makedirs("data/annotated", exist_ok=True)

# ==========================================
# Load Original Dataset
# ==========================================

df = pd.read_csv(INPUT_CSV)

print("=" * 60)
print("Original Dataset Loaded")
print(df.shape)
print("=" * 60)

# ==========================================
# Read JSON Files
# ==========================================

rows = []

files = sorted(os.listdir(JSON_FOLDER))

for file in tqdm(files):

    if not file.endswith(".json"):
        continue

    json_path = os.path.join(JSON_FOLDER, file)

    try:

        with open(json_path, "r", encoding="utf-8") as f:
            annotation = json.load(f)

        # Dataset index stored in JSON
        index = annotation["dataset_index"]

        # Original resume
        resume = df.loc[index]

        # Merge data
        row = {
            "dataset_index": index,
            "filename": resume["filename"],
            "file_path": resume["file_path"],
            "resume_text": resume["resume_text"]
        }

        # Add annotation fields
        row.update(annotation)

        rows.append(row)

    except Exception as e:

        print(f"Error in {file}")
        print(e)

# ==========================================
# Create DataFrame
# ==========================================

final_df = pd.DataFrame(rows)

print("=" * 60)
print("DataFrame Created")
print(final_df.shape)
print("=" * 60)

# ==========================================
# Save CSV
# ==========================================

final_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n✅ CSV Saved : {OUTPUT_CSV}")