import os
import json
from collections import Counter, defaultdict

# ==========================================
# Folder
# ==========================================

FAILED_FOLDER = "data/failed_annotations"

# ==========================================
# Expected Keys
# ==========================================

REQUIRED_KEYS = [
    "skills",
    "education",
    "experience_years",
    "projects",
    "certifications",

    "job_role_1",
    "confidence_1",

    "job_role_2",
    "confidence_2",

    "job_role_3",
    "confidence_3",

    "job_role_4",
    "confidence_4",

    "job_role_5",
    "confidence_5",

    "dataset_index",
    "filename",
    "file_path"
]

# ==========================================
# Statistics
# ==========================================

missing_counter = Counter()
missing_pattern_counter = Counter()

files_missing_one = []
files_missing_two = []
files_missing_three_plus = []

# ==========================================
# Read Files
# ==========================================

for file in os.listdir(FAILED_FOLDER):

    if not file.endswith(".json"):
        continue

    if file.endswith("_duplicate.json"):
        continue

    path = os.path.join(FAILED_FOLDER, file)

    try:
        with open(path, "r", encoding="utf-8") as f:
            annotation = json.load(f)

    except Exception:
        continue

    missing = []

    for key in REQUIRED_KEYS:
        if key not in annotation:
            missing.append(key)
            missing_counter[key] += 1

    if len(missing) == 0:
        continue

    pattern = tuple(sorted(missing))
    missing_pattern_counter[pattern] += 1

    if len(missing) == 1:
        files_missing_one.append((file, missing))

    elif len(missing) == 2:
        files_missing_two.append((file, missing))

    else:
        files_missing_three_plus.append((file, missing))

# ==========================================
# Results
# ==========================================

print("=" * 60)
print("FAILED ANNOTATION ANALYSIS V2")
print("=" * 60)

print("\nMost Missing Keys")
print("-" * 40)

for key, count in missing_counter.most_common():
    print(f"{key:<25} : {count}")

print("\nMost Common Missing Patterns")
print("-" * 40)

for pattern, count in missing_pattern_counter.most_common(15):
    print(f"{pattern} : {count}")

print("\nFiles Missing Exactly One Key :", len(files_missing_one))
print("Files Missing Exactly Two Keys :", len(files_missing_two))
print("Files Missing Three or More :", len(files_missing_three_plus))

print("=" * 60)