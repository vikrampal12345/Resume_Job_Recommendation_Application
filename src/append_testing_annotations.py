import os
import json
import pandas as pd

# =====================================================
# Paths
# =====================================================

ANNOTATED_CSV = "data/annotated/annotated_resume.csv"
TESTING_FOLDER = "data/testing_annotations"

# =====================================================
# Load Existing CSV
# =====================================================

df = pd.read_csv(ANNOTATED_CSV)

print(f"Existing Rows : {len(df)}")

# Existing dataset_index values
existing_indexes = set(df["dataset_index"])

# =====================================================
# Read Only New JSON Files
# =====================================================

new_rows = []
skipped = 0

for file in os.listdir(TESTING_FOLDER):

    if not file.endswith(".json"):
        continue

    path = os.path.join(TESTING_FOLDER, file)

    with open(path, "r", encoding="utf-8") as f:
        annotation = json.load(f)

    dataset_index = annotation["dataset_index"]

    # Skip if already present
    if dataset_index in existing_indexes:
        skipped += 1
        continue

    new_rows.append(annotation)

print(f"New JSON Found      : {len(new_rows)}")
print(f"Already Appended    : {skipped}")

# =====================================================
# Nothing New
# =====================================================

if len(new_rows) == 0:

    print("\nNo New Annotation Found.")
    exit()

# =====================================================
# Merge
# =====================================================

new_df = pd.DataFrame(new_rows)

merged_df = pd.concat(
    [df, new_df],
    ignore_index=True
)

# =====================================================
# Final Safety Check
# =====================================================

merged_df.drop_duplicates(
    subset="dataset_index",
    keep="first",
    inplace=True
)

merged_df.sort_values(
    by="dataset_index",
    inplace=True
)

merged_df.reset_index(
    drop=True,
    inplace=True
)

# =====================================================
# Save
# =====================================================

merged_df.to_csv(
    ANNOTATED_CSV,
    index=False
)

print("\n" + "=" * 50)
print("Merge Completed")
print("=" * 50)
print(f"Previous Rows      : {len(df)}")
print(f"New Rows Added     : {len(new_df)}")
print(f"Final Rows         : {len(merged_df)}")