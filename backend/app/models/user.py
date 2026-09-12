from datetime import datetime

from app.services.database import users_collection


def create_user_document(
    name: str,
    email: str,
    password_hash: str
):

    return {
        "name": name,
        "email": email,
        "password_hash": password_hash,

        "phone": "",
        "location": "",
        "role": "",
        "education": "",
        "experience": "Fresher",
        "bio": "",

        "skills": [],

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def get_user_by_email(email: str):

    return users_collection.find_one({
        "email": email.lower().strip()
    })


def get_user_by_id(user_id):

    return users_collection.find_one({
        "_id": user_id
    })