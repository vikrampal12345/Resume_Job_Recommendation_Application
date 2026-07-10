# ==========================================
# Required Keys
# ==========================================

required_keys = [
    "skills",
    "education",
    "experience_years",
    "projects",
    "certifications",
    "job_role_1",
    "confidence_1",
    "job_role_2",
    "confidence_2",
    "job_role_3",
    "confidence_3",
    "job_role_4",
    "confidence_4",
    "job_role_5",
    "confidence_5"
]


def validate_annotation(data):
    """
    Validate one annotated resume.
    Returns True if valid, otherwise False.
    """

    # ==========================================
    # Check Required Keys
    # ==========================================

    for key in required_keys:

        if key not in data:

            print(f"Missing Key : {key}")

            return False

    # ==========================================
    # Data Types
    # ==========================================

    if not isinstance(data["skills"], list):
        print("skills should be list")
        return False

    if not isinstance(data["projects"], list):
        print("projects should be list")
        return False

    if not isinstance(data["certifications"], list):
        print("certifications should be list")
        return False

    if not isinstance(data["education"], str):
        print("education should be string")
        return False

    if not isinstance(data["experience_years"], int):
        print("experience_years should be integer")
        return False

    # ==========================================
    # Confidence
    # ==========================================

    for i in range(1, 6):

        key = f"confidence_{i}"

        if not isinstance(data[key], int):

            print(f"{key} should be integer")

            return False

        if data[key] < 0 or data[key] > 100:

            print(f"{key} out of range")

            return False

    # ==========================================
    # Job Roles
    # ==========================================

    for i in range(1, 6):

        key = f"job_role_{i}"

        if not isinstance(data[key], str):

            print(f"{key} should be string")

            return False

        if len(data[key].strip()) == 0:

            print(f"{key} is empty")

            return False

    # ==========================================
    # Skills Length
    # ==========================================

    if len(data["skills"]) > 10:

        print("Too many skills")

        return False

    # ==========================================
    # Certification Length
    # ==========================================

    if len(data["certifications"]) > 5:

        print("Too many certifications")

        return False

    # ==========================================
    # Project Length
    # ==========================================

    if len(data["projects"]) > 5:

        print("Too many projects")

        return False

    return True

