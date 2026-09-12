import re
from typing import Dict, Any, List


# ---------------------------------------------------------
# Resume-specific signals
# ---------------------------------------------------------

RESUME_SECTIONS = {
    "experience": [
        "work experience",
        "professional experience",
        "employment history",
        "experience",
        "work history",
    ],
    "education": [
        "education",
        "academic background",
        "educational qualification",
        "qualifications",
    ],
    "skills": [
        "technical skills",
        "skills",
        "core skills",
        "key skills",
        "competencies",
        "technologies",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
    ],
    "internships": [
        "internship",
        "internships",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses",
    ],
    "achievements": [
        "achievements",
        "awards",
        "honors",
        "accomplishments",
    ],
    "summary": [
        "professional summary",
        "career summary",
        "profile",
        "objective",
        "career objective",
        "summary",
    ],
    "publications": [
        "publications",
        "research",
        "papers",
    ],
    "volunteering": [
        "volunteering",
        "volunteer experience",
        "community service",
    ],
}


# ---------------------------------------------------------
# Signals that strongly suggest the document is NOT a resume
# ---------------------------------------------------------

NON_RESUME_PATTERNS = {
    "JOB_DESCRIPTION": [
        r"\bjob description\b",
        r"\bjob responsibilities\b",
        r"\bkey responsibilities\b",
        r"\brole responsibilities\b",
        r"\bresponsibilities include\b",
        r"\bwhat you will do\b",
        r"\bwhat you'll do\b",
        r"\bwhat we are looking for\b",
        r"\bwhat we're looking for\b",
        r"\bqualifications required\b",
        r"\brequirements\b",
        r"\babout the role\b",
        r"\babout this position\b",
        r"\bjob requirements\b",
    ],
    "COVER_LETTER": [
        r"\bdear hiring manager\b",
        r"\bdear recruiter\b",
        r"\bdear sir\b",
        r"\bdear madam\b",
        r"\bdear\s+[a-z]+\b",
        r"\bsincerely\b",
        r"\bbest regards\b",
        r"\bkind regards\b",
        r"\bthank you for considering my application\b",
        r"\bi am writing to apply\b",
        r"\bi am excited to apply\b",
    ],
    "CERTIFICATE": [
        r"\bcertificate of completion\b",
        r"\bcertificate of achievement\b",
        r"\bthis is to certify\b",
        r"\bhas successfully completed\b",
        r"\bcertificate is hereby awarded\b",
        r"\bcertified that\b",
    ],
}


# ---------------------------------------------------------
# Contact / candidate identity signals
# ---------------------------------------------------------

EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)"
)

LINKEDIN_PATTERN = re.compile(
    r"\blinkedin\b",
    re.IGNORECASE,
)

GITHUB_PATTERN = re.compile(
    r"\bgithub\b",
    re.IGNORECASE,
)

PORTFOLIO_PATTERN = re.compile(
    r"\bportfolio\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# Candidate-oriented language
# ---------------------------------------------------------

CANDIDATE_LANGUAGE = [
    r"\bmy experience\b",
    r"\bmy skills\b",
    r"\bmy projects\b",
    r"\bi have\b",
    r"\bi worked\b",
    r"\bi developed\b",
    r"\bi built\b",
    r"\bi managed\b",
    r"\bi led\b",
    r"\bi implemented\b",
    r"\bworked as\b",
    r"\bcurrently working\b",
    r"\bexperience in\b",
    r"\bproficient in\b",
    r"\bskilled in\b",
    r"\bexpertise in\b",
]


# ---------------------------------------------------------
# Job-oriented language
# ---------------------------------------------------------

JOB_LANGUAGE = [
    r"\bwe are looking for\b",
    r"\bwe're looking for\b",
    r"\byou will\b",
    r"\byou'll\b",
    r"\bcandidate should\b",
    r"\bcandidate must\b",
    r"\bthe candidate\b",
    r"\bresponsible for\b",
    r"\bresponsibilities include\b",
    r"\brequired skills\b",
    r"\bpreferred skills\b",
    r"\bminimum qualifications\b",
]


# ---------------------------------------------------------
# Education signals
# ---------------------------------------------------------

DEGREE_PATTERNS = [
    r"\bbachelor(?:'s)?\b",
    r"\bmaster(?:'s)?\b",
    r"\bb\.?tech\b",
    r"\bm\.?tech\b",
    r"\bb\.?e\.?\b",
    r"\bm\.?e\.?\b",
    r"\bbca\b",
    r"\bmca\b",
    r"\bbba\b",
    r"\bmba\b",
    r"\bphd\b",
    r"\bdiploma\b",
]


# ---------------------------------------------------------
# Experience / date signals
# ---------------------------------------------------------

EXPERIENCE_PATTERNS = [
    r"\b\d+\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience\b",
    r"\b\d+\+?\s*(?:months?|mos?)\s+(?:of\s+)?experience\b",
]

DATE_RANGE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}\b"
    r"|\b(?:19|20)\d{2}\s*[-–]\s*(?:present|current)\b",
    re.IGNORECASE,
)


def _normalize_text(text: str) -> str:
    """
    Normalize text while preserving enough structure for detection.
    """
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize repeated spaces but preserve newlines.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _contains_exact_phrase(text: str, phrase: str) -> bool:
    """
    Safer phrase matching.

    Prevents things like:
        'c'
    from matching every occurrence of the letter c.
    """
    if len(phrase) <= 2:
        return bool(
            re.search(
                rf"(?<![A-Za-z0-9+#.-]){re.escape(phrase)}(?![A-Za-z0-9+#.-])",
                text,
                re.IGNORECASE,
            )
        )

    return phrase.lower() in text.lower()


def _find_resume_sections(text: str) -> Dict[str, List[str]]:
    """
    Find resume section headings/signals.
    """
    results = {}

    lower_text = text.lower()

    for section, phrases in RESUME_SECTIONS.items():
        matched = []

        for phrase in phrases:
            if _contains_exact_phrase(lower_text, phrase):
                matched.append(phrase)

        if matched:
            results[section] = matched

    return results


def _find_negative_document_types(text: str) -> Dict[str, List[str]]:
    """
    Detect documents that are clearly not resumes.
    """
    results = {}

    for document_type, patterns in NON_RESUME_PATTERNS.items():
        matches = []

        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)

            if found:
                matches.extend(found)

        if matches:
            results[document_type] = matches

    return results


def _count_patterns(text: str, patterns: List[str]) -> int:
    count = 0

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            count += 1

    return count


def _candidate_identity_signals(text: str) -> Dict[str, Any]:
    return {
        "email": bool(EMAIL_PATTERN.search(text)),
        "phone": bool(PHONE_PATTERN.search(text)),
        "linkedin": bool(LINKEDIN_PATTERN.search(text)),
        "github": bool(GITHUB_PATTERN.search(text)),
        "portfolio": bool(PORTFOLIO_PATTERN.search(text)),
    }


def _calculate_score(
    text: str,
    sections: Dict[str, List[str]],
    negative_types: Dict[str, List[str]],
    identity_signals: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0
    positive_reasons = []
    negative_reasons = []

    # -----------------------------------------------------
    # Resume section evidence
    # -----------------------------------------------------

    section_count = len(sections)

    if section_count >= 5:
        score += 40
        positive_reasons.append("multiple_resume_sections")

    elif section_count >= 3:
        score += 30
        positive_reasons.append("several_resume_sections")

    elif section_count >= 2:
        score += 20
        positive_reasons.append("multiple_resume_sections")

    elif section_count == 1:
        score += 8
        positive_reasons.append("one_resume_section")

    # Strong combinations
    if "experience" in sections and "skills" in sections:
        score += 10
        positive_reasons.append("experience_and_skills")

    if "education" in sections and "experience" in sections:
        score += 8
        positive_reasons.append("education_and_experience")

    if "projects" in sections and "skills" in sections:
        score += 7
        positive_reasons.append("projects_and_skills")

    # -----------------------------------------------------
    # Candidate identity
    # -----------------------------------------------------

    identity_count = sum(
        1 for value in identity_signals.values() if value
    )

    if identity_count >= 3:
        score += 18
        positive_reasons.append("strong_contact_profile")

    elif identity_count >= 2:
        score += 12
        positive_reasons.append("candidate_contact_information")

    elif identity_count == 1:
        score += 5
        positive_reasons.append("candidate_contact_signal")

    # -----------------------------------------------------
    # Candidate language
    # -----------------------------------------------------

    candidate_language_count = _count_patterns(
        text,
        CANDIDATE_LANGUAGE,
    )

    if candidate_language_count >= 4:
        score += 12
        positive_reasons.append("candidate_oriented_language")

    elif candidate_language_count >= 2:
        score += 7
        positive_reasons.append("candidate_language")

    # -----------------------------------------------------
    # Education / experience signals
    # -----------------------------------------------------

    degree_count = _count_patterns(
        text,
        DEGREE_PATTERNS,
    )

    if degree_count >= 1:
        score += 7
        positive_reasons.append("education_signal")

    experience_count = _count_patterns(
        text,
        EXPERIENCE_PATTERNS,
    )

    date_ranges = len(DATE_RANGE_PATTERN.findall(text))

    if experience_count >= 1:
        score += 8
        positive_reasons.append("experience_duration")

    if date_ranges >= 1:
        score += 5
        positive_reasons.append("employment_date_range")

    # -----------------------------------------------------
    # Negative document signals
    # -----------------------------------------------------

    if "JOB_DESCRIPTION" in negative_types:
        score -= 35
        negative_reasons.append("job_description_language")

    if "COVER_LETTER" in negative_types:
        score -= 40
        negative_reasons.append("cover_letter_language")

    if "CERTIFICATE" in negative_types:
        score -= 40
        negative_reasons.append("certificate_language")

    job_language_count = _count_patterns(
        text,
        JOB_LANGUAGE,
    )

    if job_language_count >= 4:
        score -= 20
        negative_reasons.append("strong_job_oriented_language")

    elif job_language_count >= 2:
        score -= 10
        negative_reasons.append("job_oriented_language")

    # Keep score in predictable range.
    score = max(0, min(100, score))

    return {
        "score": score,
        "positive_reasons": positive_reasons,
        "negative_reasons": negative_reasons,
        "candidate_language_count": candidate_language_count,
        "job_language_count": job_language_count,
        "degree_count": degree_count,
        "experience_count": experience_count,
        "date_range_count": date_ranges,
    }


def _detect_document_type(
    negative_types: Dict[str, List[str]],
    sections: Dict[str, List[str]],
) -> str:

    # Strong explicit document types first.
    if "CERTIFICATE" in negative_types:
        return "CERTIFICATE"

    if "COVER_LETTER" in negative_types:
        return "COVER_LETTER"

    if "JOB_DESCRIPTION" in negative_types:
        # If there are strong resume sections too, don't blindly
        # call it a JD. It may be a mixed document.
        if len(sections) >= 3:
            return "MIXED_DOCUMENT"

        return "JOB_DESCRIPTION"

    if len(sections) >= 2:
        return "RESUME"

    if len(sections) == 1:
        return "POSSIBLE_RESUME"

    return "UNKNOWN"


def _make_reason(
    classification: str,
    document_type: str,
    score: int,
    positive_reasons: List[str],
    negative_reasons: List[str],
) -> str:

    if classification == "RESUME_RELEVANT":
        return (
            "The document contains multiple candidate/resume signals "
            f"and was classified as resume-relevant with a score of {score}/100."
        )

    if classification == "NOT_A_RESUME":
        if document_type != "UNKNOWN":
            return (
                f"The document appears to be a {document_type.replace('_', ' ').lower()}, "
                "not a candidate resume."
            )

        return (
            "The document does not contain enough reliable resume signals "
            "to continue the resume analysis pipeline."
        )

    return (
        "The document contains some resume-like signals, but they are not "
        "strong enough to safely continue automatic resume analysis."
    )


def filter_resume_relevance(text: str) -> Dict[str, Any]:
    """
    Main Resume Relevance Filter.

    Output:
        is_resume
        classification
        confidence
        score
        document_type
        reason
        continue_pipeline
        signals
    """

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return {
            "is_resume": False,
            "classification": "NOT_A_RESUME",
            "confidence": 1.0,
            "score": 0,
            "document_type": "EMPTY_DOCUMENT",
            "reason": "No readable text could be extracted from the uploaded document.",
            "continue_pipeline": False,
            "signals": {},
        }

    # Very short documents should not enter the expensive pipeline.
    if len(normalized_text) < 80:
        return {
            "is_resume": False,
            "classification": "NOT_A_RESUME",
            "confidence": 0.95,
            "score": 0,
            "document_type": "INSUFFICIENT_TEXT",
            "reason": (
                "The extracted document contains too little readable text "
                "to be considered a valid resume."
            ),
            "continue_pipeline": False,
            "signals": {
                "character_count": len(normalized_text),
            },
        }

    sections = _find_resume_sections(normalized_text)

    negative_types = _find_negative_document_types(
        normalized_text
    )

    identity_signals = _candidate_identity_signals(
        normalized_text
    )

    scoring = _calculate_score(
        normalized_text,
        sections,
        negative_types,
        identity_signals,
    )

    score = scoring["score"]

    document_type = _detect_document_type(
        negative_types,
        sections,
    )

    # -----------------------------------------------------
    # Hard rejection
    # -----------------------------------------------------

    hard_reject_types = {
        "JOB_DESCRIPTION",
        "COVER_LETTER",
        "CERTIFICATE",
        "MIXED_DOCUMENT",
        "EMPTY_DOCUMENT",
        "INSUFFICIENT_TEXT",
    }

    if document_type in hard_reject_types:
        classification = "NOT_A_RESUME"
        continue_pipeline = False

    # -----------------------------------------------------
    # Classification thresholds
    # -----------------------------------------------------

    elif score >= 65:
        classification = "RESUME_RELEVANT"
        continue_pipeline = True

    elif score >= 45:
        classification = "UNCERTAIN"
        continue_pipeline = False

    else:
        classification = "NOT_A_RESUME"
        continue_pipeline = False

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    if classification == "RESUME_RELEVANT":
        confidence = min(
            0.99,
            0.65 + ((score - 65) / 100),
        )

    elif classification == "NOT_A_RESUME":
        confidence = min(
            0.99,
            0.70 + ((65 - score) / 100),
        )

    else:
        confidence = 0.50 + abs(score - 54) / 100

    confidence = round(
        max(0.50, min(0.99, confidence)),
        2,
    )

    reason = _make_reason(
        classification,
        document_type,
        score,
        scoring["positive_reasons"],
        scoring["negative_reasons"],
    )

    return {
        "is_resume": classification == "RESUME_RELEVANT",
        "classification": classification,
        "confidence": confidence,
        "score": score,
        "document_type": document_type,
        "reason": reason,
        "continue_pipeline": continue_pipeline,
        "signals": {
            "character_count": len(normalized_text),
            "resume_sections": sections,
            "negative_document_types": negative_types,
            "identity_signals": identity_signals,
            "positive_reasons": scoring["positive_reasons"],
            "negative_reasons": scoring["negative_reasons"],
            "candidate_language_count": scoring[
                "candidate_language_count"
            ],
            "job_language_count": scoring[
                "job_language_count"
            ],
            "degree_count": scoring["degree_count"],
            "experience_count": scoring["experience_count"],
            "date_range_count": scoring["date_range_count"],
        },
    }