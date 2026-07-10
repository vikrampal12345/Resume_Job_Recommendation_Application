import os
import json
import pandas as pd
from openai import OpenAI

from config import *
from prompt import build_prompt
from parser import parse_json
from validator import validate_annotation
from tqdm import tqdm
import time


# ================================
# Connect LM Studio
# ================================

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

# ================================
# Load Dataset
# ================================

df = pd.read_csv(INPUT_CSV)

print("="*60)
print("Dataset Loaded")
print(df.shape)
print("="*60)

# ================================
# Create Output Folder
# ================================

OUTPUT_FOLDER = "data/annotations"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

FAILED_FOLDER = "data/failed_annotations"

os.makedirs(FAILED_FOLDER, exist_ok=True)

# ==========================================
# Process Resume One By One
# ==========================================
# ==========================================
# Statistics
# ==========================================
start_time = time.time()
saved = 0
failed = 0
api_failed = 0
json_failed = 0
duplicate_failed = 0
END_INDEX = min(END_INDEX, len(df))
for i in tqdm(range(START_INDEX, END_INDEX)):

    print("\n" + "="*60)
    print(f"Resume {i}")
    print("="*60)

    resume_text = str(df.loc[i, "resume_text"])

    prompt = build_prompt([resume_text])

    success = False

    for attempt in range(MAX_RETRIES):

        try:

            response = client.chat.completions.create(

                model=MODEL_NAME,

                temperature=TEMPERATURE,

                max_tokens=MAX_TOKENS,

                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]

            )

            success = True
            break

        except Exception as e:

            print(f"Attempt {attempt+1} Failed")

            time.sleep(SLEEP_TIME)

    if not success:

        api_failed += 1

        failed_file = os.path.join(
            FAILED_FOLDER,
            f"resume_{i:06d}_api_error.txt"
        )

        if not os.path.exists(failed_file):

            with open(failed_file, "w", encoding="utf-8") as f:
                f.write(str(e))

        print(f"❌ API Error : {e}")

        continue

    output = response.choices[0].message.content

    

    data = parse_json(output)

    if data is None:

        json_failed += 1

        failed_file = os.path.join(
            FAILED_FOLDER,
            f"resume_{i:06d}_invalid_json.txt"
        )
        if not os.path.exists(failed_file):
            with open(failed_file, "w", encoding="utf-8") as f:
                f.write(output)

        print("❌ Invalid JSON")

        continue

    print("✅ JSON Parsed")

    # ------------------------------------
# Exactly one JSON object is expected
# ------------------------------------
    if not isinstance(data, list):

        json_failed += 1

        failed_file = os.path.join(
            FAILED_FOLDER,
            f"resume_{i:06d}_not_list.json"
        )
        if not os.path.exists(failed_file):
            with open(failed_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        print("❌ Output is not a list")

        continue
    if len(data) != 1:
        duplicate_failed += 1

        failed_file = os.path.join(
            FAILED_FOLDER,
            f"resume_{i:06d}_duplicate.json"
        )
        if not os.path.exists(failed_file):
            with open(failed_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        continue
       
    # ==========================================
# Save JSON
# ==========================================

    json_file = os.path.join(
        OUTPUT_FOLDER,
        f"resume_{i:06d}.json"
    )

    # Skip if already exists
    if os.path.exists(json_file):
        print(f"⚠️ {json_file} already exists. Skipping.")
        continue
    annotation = data[0]

    annotation["dataset_index"] = i
    annotation["filename"] = df.loc[i, "filename"]
    annotation["file_path"] = df.loc[i, "file_path"]


    
    if not validate_annotation(annotation):

        failed += 1

        failed_file = os.path.join(
            FAILED_FOLDER,
            f"resume_{i:06d}.json"
        )
        if not os.path.exists(failed_file):
            with open(failed_file, "w", encoding="utf-8") as f:

                json.dump(
                    annotation,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        print(f"❌ Validation Failed : {failed_file}")

        continue
    with open(json_file, "w", encoding="utf-8") as f:

        json.dump(
            annotation,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"✅ Saved : {i} saved")
    saved += 1


end_time = time.time()

print(f"Total Time : {(end_time-start_time)/60:.2f} minutes")

print("\n" + "=" * 60)
print("Annotation Finished")
print("=" * 60)

print(f"Processed           : {END_INDEX - START_INDEX}")
print(f"Saved               : {saved}")
print(f"Validation Failed   : {failed}")
print(f"Duplicate Response  : {duplicate_failed}")
print(f"Invalid JSON        : {json_failed}")
print(f"API Failed          : {api_failed}")
print(f"Total Time          : {(end_time-start_time)/60:.2f} minutes")

print("=" * 60)