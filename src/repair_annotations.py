import os
import json
import pandas as pd
from tqdm import tqdm

from validator import validate_annotation

# =====================================================
# Folders
# =====================================================

FAILED_FOLDER = "data/failed_annotations"
TESTING_FOLDER = "data/testing_annotations"

os.makedirs(TESTING_FOLDER, exist_ok=True)

# =====================================================
# Statistics
# =====================================================

total_files = 0
fixed_negative_key = 0
fixed_than_key = 0
fixed_duplicate = 0
repaired = 0
still_failed = 0

reannotation_queue = []

# =====================================================
# Read All Failed Files
# =====================================================

files = sorted(os.listdir(FAILED_FOLDER))

for file in tqdm(files):

    if not file.endswith(".json"):
        continue

    failed_path = os.path.join(FAILED_FOLDER, file)
    output_path = os.path.join(TESTING_FOLDER, file)

    # -----------------------------------------------
    # Skip if already repaired
    # -----------------------------------------------

    if os.path.exists(output_path):
        continue

    total_files += 1

    # -----------------------------------------------
    # Read JSON
    # -----------------------------------------------

    try:

        with open(failed_path, "r", encoding="utf-8") as f:
            annotation = json.load(f)

    except Exception:

        reannotation_queue.append({

            "failed_json": file,
            "reason": "Invalid JSON"

        })

        still_failed += 1
        continue

    repaired_this_file = False

    # =====================================================
    # Fix Duplicate JSON
    # =====================================================

    if isinstance(annotation, list):

        if len(annotation) != 2:

            still_failed += 1
            continue

        if annotation[0] == annotation[1]:

            annotation = annotation[0]

            repaired_this_file = True
            fixed_duplicate += 1

        

        else:

            reannotation_queue.append({

                "failed_json": file,
                "reason": "duplicate objests different"

            })

            still_failed += 1
            continue

    # =====================================================
    # Fix job_role_-1 ... job_role_-5
    # =====================================================

    for i in range(1, 6):

        wrong_key = f"job_role_-{i}"
        correct_key = f"job_role_{i}"

        if wrong_key in annotation:

            annotation[correct_key] = annotation.pop(wrong_key)

            repaired_this_file = True
            fixed_negative_key += 1

    # =====================================================
    # Fix job_role_-than
    # =====================================================

    if "job_role_-than" in annotation:

        annotation["job_role_4"] = annotation.pop("job_role_-than")

        repaired_this_file = True
        fixed_than_key += 1

    # =====================================================
    # Validate
    # =====================================================

    if repaired_this_file:

        if validate_annotation(annotation):

            with open(output_path, "w", encoding="utf-8") as f:

                json.dump(
                    annotation,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            # Remove repaired file from failed folder
            os.remove(failed_path)

            repaired += 1

        else:

            reannotation_queue.append({

                "failed_json": file,
                "dataset_index": annotation.get("dataset_index"),
                "filename": annotation.get("filename"),
                "file_path": annotation.get("file_path")

            })

            still_failed += 1


    # if repaired_this_file:

    #     if validate_annotation(annotation):

    #         print(f"PASS : {file}")

    #         ...
    #     else:

    #         print(f"FAIL : {file}")

    #         required = [
    #             "job_role_1","confidence_1",
    #             "job_role_2","confidence_2",
    #             "job_role_3","confidence_3",
    #             "job_role_4","confidence_4",
    #             "job_role_5","confidence_5",
    #             "dataset_index",
    #             "filename",
    #             "file_path"
    #         ]

    #         for key in required:
    #             if key not in annotation:
    #                 print("Missing ->", key)

    #         break

# =====================================================
# Save Reannotation Queue
# =====================================================

if len(reannotation_queue) > 0:

    queue_df = pd.DataFrame(reannotation_queue)

    queue_df.to_csv(
        "data/reannotation_queue.csv",
        index=False
    )

# =====================================================
# Summary
# =====================================================

print("\n" + "=" * 60)
print("Repair Summary")
print("=" * 60)

print(f"Total Failed Files      : {total_files}")
print(f"Negative Keys Fixed     : {fixed_negative_key}")
print(f"'-than' Keys Fixed      : {fixed_than_key}")
print(f"Duplicate Fixed         : {fixed_duplicate}")
print(f"Successfully Repaired   : {repaired}")
print(f"Still Failed            : {still_failed}")
print(f"Testing Folder Saved    : {repaired}")
print(f"Reannotation Queue      : {len(reannotation_queue)}")

print("=" * 60)