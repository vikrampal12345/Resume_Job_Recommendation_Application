from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.database import (
    users_collection
)

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class SignupRequest(BaseModel):

    name: str
    email: EmailStr
    password: str
    confirmPassword: str


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


@router.post("/signup")
def signup(request: SignupRequest):

    name = request.name.strip()

    email = (
        str(request.email)
        .lower()
        .strip()
    )

    if not name:

        raise HTTPException(
            status_code=400,
            detail="Name is required."
        )

    if len(request.password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters."
        )

    if (
        request.password
        != request.confirmPassword
    ):

        raise HTTPException(
            status_code=400,
            detail="Passwords do not match."
        )

    existing_user = users_collection.find_one({
        "email": email
    })

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    password_hash = hash_password(
        request.password
    )

    result = users_collection.insert_one({
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

        "created_at": __import__(
            "datetime"
        ).datetime.utcnow(),

        "updated_at": __import__(
            "datetime"
        ).datetime.utcnow()
    })

    token = create_access_token(
        result.inserted_id
    )

    return {
        "success": True,
        "message": "Account created successfully.",
        "token": token,
        "user": {
            "id": str(
                result.inserted_id
            ),
            "name": name,
            "email": email
        }
    }


@router.post("/login")
def login(request: LoginRequest):

    email = (
        str(request.email)
        .lower()
        .strip()
    )

    user = users_collection.find_one({
        "email": email
    })

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        request.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_access_token(
        user["_id"]
    )

    return {
        "success": True,
        "message": "Login successful.",
        "token": token,

        "user": {
            "id": str(
                user["_id"]
            ),
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.post("/logout")
def logout():

    return {
        "success": True,
        "message": "Logout successful."
    }