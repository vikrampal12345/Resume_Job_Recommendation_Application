import os
import json
import pandas as pd
from openai import OpenAI

from config import *
from prompt import build_prompt
from parser import parse_json
from validator import validate_annotation


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


# ==========================================
# Process Resume One By One
# ==========================================

for i in range(LIMIT):

    print("\n" + "="*60)
    print(f"Resume {i+1}")
    print("="*60)

    resume_text = str(df.loc[i, "resume_text"])

    prompt = build_prompt([resume_text])

    response = client.chat.completions.create(

        model=MODEL_NAME,

        temperature=TEMPERATURE,

        max_tokens=MAX_TOKENS,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    output = response.choices[0].message.content

    print(output)