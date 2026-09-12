import os
from datetime import datetime, timedelta, timezone

import bcrypt

from jose import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-this-secret"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

JWT_EXPIRE_DAYS = int(
    os.getenv(
        "JWT_EXPIRE_DAYS",
        "7"
    )
)


def hash_password(password: str):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    password: str,
    password_hash: str
):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def create_access_token(user_id):

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        days=JWT_EXPIRE_DAYS
    )

    payload = {
        "user_id": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str):

    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM]
    )