import os
import json

FAILED_FOLDER = "data/failed_annotations"

same = 0
different = 0
invalid = 0

for file in os.listdir(FAILED_FOLDER):

    if not file.endswith("_duplicate.json"):
        continue

    path = os.path.join(FAILED_FOLDER, file)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            invalid += 1
            continue

        if len(data) != 2:
            invalid += 1
            continue

        if data[0] == data[1]:
            same += 1
        else:
            different += 1

    except Exception:
        invalid += 1

print("=" * 50)
print(f"Same Duplicate      : {same}")
print(f"Different Duplicate : {different}")
print(f"Invalid Duplicate   : {invalid}")
print("=" * 50)