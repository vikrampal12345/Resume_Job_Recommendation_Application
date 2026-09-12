import os

from pymongo import MongoClient
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        ".env"
    )
)


# =========================================================
# MONGODB CONFIGURATION
# =========================================================

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv(
    "MONGO_DATABASE",
    "syncronal"
)


# =========================================================
# MONGODB CLIENT
# =========================================================

client = None
db = None


def get_database():
    """
    Return the MongoDB database instance.

    MongoDB connection is created lazily so the backend
    can still start while MongoDB configuration is not
    available yet.
    """

    global client
    global db

    if db is not None:
        return db

    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI is not configured in app/.env"
        )

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Force a connection check
    client.admin.command("ping")

    db = client[MONGO_DATABASE]

    return db


# =========================================================
# COLLECTIONS
# =========================================================

def get_resume_analyses_collection():
    """
    Collection used to store resume analysis history.
    """

    database = get_database()

    return database["resume_analyses"]


def get_applications_collection():
    """
    Collection used to store applied-job history.
    """

    database = get_database()

    return database["applications"]