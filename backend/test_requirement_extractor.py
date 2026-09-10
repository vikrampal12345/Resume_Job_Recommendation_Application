import json
from app.requirement_extractor import extract_requirements


def test_requirement_extraction():
    jd = """
    Backend Developer
    Qualifications:
    - 2+ years of experience with Python and FastAPI.
    - REST APIs are required.
    - Docker is preferred.
    - AWS is a plus.
    - Kubernetes is nice to have.
    """
    result = extract_requirements(jd, use_llm=False)
    by_skill = {r["skill"].lower(): r for r in result["requirements"]}

    assert result["experience"]["minimum_years"] == 2
    assert by_skill["python"]["importance"] in {"REQUIRED", "UNKNOWN"}
    assert by_skill["fastapi"]["importance"] in {"REQUIRED", "UNKNOWN"}
    assert by_skill["docker"]["importance"] == "PREFERRED"
    assert by_skill["kubernetes"]["importance"] == "NICE_TO_HAVE"


if __name__ == "__main__":
    print(json.dumps(extract_requirements(jd if False else "Python required; Docker preferred; 2+ years experience.", use_llm=False), indent=2))
