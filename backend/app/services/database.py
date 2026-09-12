import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "syncronal")

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

users_collection = db["users"]
resumes_collection = db["resumes"]
applications_collection = db["applications"]
saved_jobs_collection = db["saved_jobs"]


def init_db():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")

        # Optional indexes
        users_collection.create_index("email", unique=True)
        resumes_collection.create_index("user_id")
        applications_collection.create_index("user_id")
        saved_jobs_collection.create_index(
            [("user_id", 1), ("job_id", 1)],
            unique=True
        )

    except Exception as e:
        print("MongoDB connection failed:")
        print(e)