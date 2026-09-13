import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from dotenv import load_dotenv


# =========================================
# LOAD ENVIRONMENT VARIABLES
# =========================================

load_dotenv()


# =========================================
# JWT CONFIGURATION
# =========================================

JWT_SECRET = os.getenv("JWT_SECRET")

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


# =========================================
# CONFIGURATION CHECK
# =========================================

print(
    "JWT_SECRET loaded:",
    bool(JWT_SECRET)
)

print(
    "JWT_ALGORITHM:",
    JWT_ALGORITHM
)

print(
    "JWT_EXPIRE_DAYS:",
    JWT_EXPIRE_DAYS
)


# =========================================
# PASSWORD HASHING
# =========================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


# =========================================
# PASSWORD VERIFICATION
# =========================================

def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =========================================
# CREATE ACCESS TOKEN
# =========================================

def create_access_token(user_id) -> str:
    """
    Creates a new JWT token for a user.
    """

    if not JWT_SECRET:
        raise RuntimeError(
            "JWT_SECRET is not configured."
        )

    expire = (
        datetime.now(timezone.utc)
        + timedelta(days=JWT_EXPIRE_DAYS)
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return token


# =========================================
# DECODE / VERIFY ACCESS TOKEN
# =========================================

def decode_access_token(token: str):
    """
    Decodes and verifies an existing JWT token.

    Returns:
        payload -> valid token
        None    -> invalid/expired token
    """

    if not JWT_SECRET:
        print(
            "JWT decode failed: JWT_SECRET is not configured."
        )
        return None

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        print(
            "JWT decode failed: Token has expired."
        )

        return None

    except jwt.JWTError as error:

        print(
            "JWT decode failed:",
            error
        )

        return None

    except Exception as error:

        print(
            "JWT decode failed:",
            error
        )

        return None