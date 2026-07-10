# ==========================================
# Model Configuration
# ==========================================

MODEL_NAME = "qwen/qwen3-4b-2507"

BASE_URL = "http://127.0.0.1:1234/v1"

API_KEY = "lm-studio"

# ==========================================
# Dataset
# ==========================================

INPUT_CSV = "data/extracted/clean_resume.csv"

OUTPUT_CSV = "data/annotated/annotated_resume10.csv"

FAILED_CSV = "data/annotated/failed_resume.csv"

# ==========================================
# Annotation
# ==========================================

BATCH_SIZE = 1

START_INDEX = 6000
END_INDEX = 7006

TEMPERATURE = 0

MAX_TOKENS = 3000

MAX_RETRIES = 3

SLEEP_TIME = 1