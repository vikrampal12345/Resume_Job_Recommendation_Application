import json
import re

def parse_json(text):

    if text is None:
        return None

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    match = re.search(r"\[.*\]", text, flags=re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group(0))

    except json.JSONDecodeError as e:
        print("=" * 80)
        print("JSON ERROR")
        print(e)
        print("=" * 80)
        return None