"""
Syncronal Evidence Engine

Purpose
-------
Compare structured job requirements against the candidate's CURRENT resume.

Core principle
--------------
Evidence over keywords.

The engine answers:

    "What evidence does the current resume contain for this requirement?"

It does NOT decide whether the candidate should apply.

Supported logic
---------------
SINGLE
ANY_OF
ALL_OF

Evidence statuses
-----------------
DIRECT
RELATED
PARTIAL
MISSING
UNKNOWN
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    CURRENT_DIR,
    "models",
    "minilm_model",
)

FAISS_INDEX_PATH = os.path.join(
    CURRENT_DIR,
    "models",
    "resume_index.faiss",
)

RESUME_DATABASE_PATH = os.path.join(
    CURRENT_DIR,
    "models",
    "resume_database.csv",
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="[EvidenceEngine] %(message)s",
    )


# ============================================================
# STATUS CONSTANTS
# ============================================================

DIRECT = "DIRECT"
RELATED = "RELATED"
PARTIAL = "PARTIAL"
MISSING = "MISSING"
UNKNOWN = "UNKNOWN"


# ============================================================
# LOGIC CONSTANTS
# ============================================================

SINGLE = "SINGLE"
ANY_OF = "ANY_OF"
ALL_OF = "ALL_OF"


# ============================================================
# SEMANTIC THRESHOLDS
# ============================================================

DIRECT_SIMILARITY = 0.72
RELATED_SIMILARITY = 0.55
PARTIAL_SIMILARITY = 0.40


# ============================================================
# CONFIDENCE
# ============================================================

LEXICAL_DIRECT_CONFIDENCE = 0.90
LEXICAL_SECTION_CONFIDENCE = 0.96


# ============================================================
# SECTION ALIASES
# ============================================================

SECTION_ALIASES = {
    "summary": "SUMMARY",
    "profile": "SUMMARY",
    "professional summary": "SUMMARY",
    "objective": "SUMMARY",
    "career objective": "SUMMARY",
    "about": "SUMMARY",

    "skills": "SKILLS",
    "technical skills": "SKILLS",
    "technical skill": "SKILLS",
    "core skills": "SKILLS",
    "technical expertise": "SKILLS",
    "technologies": "SKILLS",
    "skills & technologies": "SKILLS",

    "experience": "EXPERIENCE",
    "work experience": "EXPERIENCE",
    "professional experience": "EXPERIENCE",
    "employment": "EXPERIENCE",
    "work history": "EXPERIENCE",

    "projects": "PROJECTS",
    "personal projects": "PROJECTS",
    "academic projects": "PROJECTS",
    "project experience": "PROJECTS",

    "education": "EDUCATION",
    "academic background": "EDUCATION",
    "qualifications": "EDUCATION",

    "certifications": "CERTIFICATIONS",
    "certificates": "CERTIFICATIONS",

    "achievements": "ACHIEVEMENTS",
    "awards": "ACHIEVEMENTS",
}


# ============================================================
# RELATED TERMS
# ============================================================
#
# IMPORTANT:
# RELATED does not mean DIRECT.
#
# Example:
# FastAPI can be related to Python,
# but FastAPI alone should not automatically become
# DIRECT evidence for Python.
# ============================================================

RELATED_TERMS = {
    "fastapi": {
        "python",
    },

    "flask": {
        "python",
    },

    "django": {
        "python",
    },

    "spring boot": {
        "spring",
        "java",
    },

    "node.js": {
        "javascript",
        "typescript",
    },

    "kubernetes": {
        "containerization",
    },

    "docker": {
        "containerization",
    },

    "postgresql": {
        "sql",
    },

    "mysql": {
        "sql",
    },

    "dynamodb": {
        "aws",
    },

    "aws lambda": {
        "aws",
    },

    "aws fargate": {
        "aws",
        "docker",
    },

    "aws eks": {
        "aws",
        "kubernetes",
    },

    "prometheus": {
        "metrics",
        "observability",
        "monitoring",
    },

    "grafana": {
        "metrics",
        "observability",
        "monitoring",
    },

    "opentelemetry": {
        "distributed tracing",
        "observability",
    },

    "distributed tracing": {
        "opentelemetry",
        "observability",
    },

    "ci/cd": {
        "continuous integration",
        "continuous deployment",
    },
}


# ============================================================
# EDUCATION
# ============================================================

EDUCATION_ALIASES = {
    "b.tech": "bachelor",
    "btech": "bachelor",
    "b.e": "bachelor",
    "be": "bachelor",
    "bachelor": "bachelor",
    "bachelor's": "bachelor",
    "bachelors": "bachelor",
    "bachelor's degree": "bachelor",
    "bachelor degree": "bachelor",

    "m.tech": "master",
    "mtech": "master",
    "m.e": "master",
    "me": "master",
    "master": "master",
    "master's": "master",
    "masters": "master",
    "master's degree": "master",
    "master degree": "master",

    "phd": "doctorate",
    "ph.d": "doctorate",
    "doctorate": "doctorate",
}


# ============================================================
# MODEL CACHE
# ============================================================

_model: Optional[SentenceTransformer] = None


# ============================================================
# BASIC TEXT HELPERS
# ============================================================

def _clean_text(value: Any) -> str:
    """
    Clean a single piece of text.

    IMPORTANT:
    This function intentionally collapses whitespace.

    Do NOT use this on the entire resume before section parsing.
    """

    if value is None:
        return ""

    value = str(value)

    value = value.replace(
        "\x00",
        " ",
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def _preserve_resume_text(
    value: Any,
) -> str:
    """
    Clean resume text WITHOUT destroying line breaks.

    This is critical for section provenance.
    """

    if value is None:
        return ""

    value = str(value)

    value = value.replace(
        "\x00",
        "",
    )

    value = value.replace(
        "\r\n",
        "\n",
    )

    value = value.replace(
        "\r",
        "\n",
    )

    # Normalize tabs but preserve newlines.
    value = re.sub(
        r"[ \t]+",
        " ",
        value,
    )

    # Avoid excessive blank lines.
    value = re.sub(
        r"\n{3,}",
        "\n\n",
        value,
    )

    return value.strip()


def _normalize_key(
    value: Any,
) -> str:

    value = _clean_text(
        value
    ).lower()

    value = value.replace(
        "–",
        "-",
    )

    value = value.replace(
        "—",
        "-",
    )

    value = re.sub(
        r"[^\w+#./& -]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================
# REQUIREMENT NAME NORMALIZATION
# ============================================================

def _normalize_requirement_name(
    value: Any,
) -> str:

    value = _clean_text(
        value
    )

    if not value:
        return ""

    key = _normalize_key(
        value
    )

    aliases = {
        "golang": "Go",
        "go lang": "Go",

        "amazon web services": "AWS",

        "gcp": "Google Cloud Platform",
        "google cloud": "Google Cloud Platform",

        "postgres": "PostgreSQL",

        "nodejs": "Node.js",
        "node js": "Node.js",

        "rest api": "REST APIs",
        "rest apis": "REST APIs",

        "open telemetry": "OpenTelemetry",

        "k8s": "Kubernetes",

        "b.tech": "Bachelor's Degree",
        "btech": "Bachelor's Degree",

        "m.tech": "Master's Degree",
        "mtech": "Master's Degree",
    }

    if key in aliases:
        return aliases[key]

    canonical = {
        "python": "Python",
        "java": "Java",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "go": "Go",
        "rust": "Rust",

        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "spring": "Spring",
        "spring boot": "Spring Boot",

        "docker": "Docker",
        "containerization": "Containerization",
        "kubernetes": "Kubernetes",

        "aws": "AWS",
        "google cloud platform": "Google Cloud Platform",
        "azure": "Azure",

        "kafka": "Kafka",
        "kinesis": "Kinesis",

        "sql": "SQL",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "redis": "Redis",

        "prometheus": "Prometheus",
        "grafana": "Grafana",
        "opentelemetry": "OpenTelemetry",

        "ci/cd": "CI/CD",

        "distributed systems": "Distributed Systems",
        "distributed data systems": "Distributed Data Systems",

        "time-series databases": "Time-series Databases",
        "time series databases": "Time-series Databases",

        "bachelor's degree": "Bachelor's Degree",
        "bachelor degree": "Bachelor's Degree",

        "master's degree": "Master's Degree",
        "master degree": "Master's Degree",
    }

    return canonical.get(
        key,
        value,
    )


# ============================================================
# LOGIC NORMALIZATION
# ============================================================

def _normalize_logic(
    value: Any,
) -> str:
    """
    Normalize logical requirement type.

    IMPORTANT FIX:
    ANY_OF and ALL_OF are explicitly preserved.
    """

    value = _clean_text(
        value
    ).upper()

    aliases = {
        "SINGLE": SINGLE,

        "ANY_OF": ANY_OF,
        "ANY": ANY_OF,
        "OR": ANY_OF,
        "ONE_OF": ANY_OF,
        "ONE OF": ANY_OF,

        "ALL_OF": ALL_OF,
        "ALL": ALL_OF,
        "AND": ALL_OF,
    }

    return aliases.get(
        value,
        SINGLE,
    )


# ============================================================
# MODEL LOADER
# ============================================================

def _load_model() -> SentenceTransformer:
    global _model

    if _model is not None:
        return _model

    logger.info(
        "Loading MiniLM model..."
    )

    if not os.path.exists(
        MODEL_PATH
    ):
        raise FileNotFoundError(
            f"MiniLM model not found at: {MODEL_PATH}"
        )

    _model = SentenceTransformer(
        MODEL_PATH
    )

    logger.info(
        "MiniLM loaded successfully."
    )

    return _model


# ============================================================
# SECTION DETECTION
# ============================================================

def _detect_section(
    line: str,
) -> Optional[str]:

    clean = _normalize_key(
        line
    )

    if not clean:
        return None

    clean = clean.strip(
        ":- "
    )

    return SECTION_ALIASES.get(
        clean
    )


# ============================================================
# SPLIT RESUME INTO SECTIONS
# ============================================================

def _split_resume_sections(
    resume_text: str,
) -> List[Dict[str, Any]]:
    """
    Preserve resume section information.

    Example:

        SUMMARY
        ...
        SKILLS
        ...
        EXPERIENCE
        ...

    becomes:

        [
            {"section": "SUMMARY", ...},
            {"section": "SKILLS", ...},
            {"section": "EXPERIENCE", ...}
        ]
    """

    lines = resume_text.splitlines()

    sections: List[
        Dict[str, Any]
    ] = []

    current_section = "GENERAL"

    current_lines: List[str] = []

    def flush():

        nonlocal current_lines

        text = "\n".join(
            current_lines
        ).strip()

        if text:

            sections.append(
                {
                    "section": current_section,
                    "text": text,
                }
            )

        current_lines = []

    for line in lines:

        section = _detect_section(
            line
        )

        if section:

            flush()

            current_section = section

            continue

        current_lines.append(
            line
        )

    flush()

    return sections


# ============================================================
# RESUME CHUNKING
# ============================================================

def _split_into_chunks(
    resume_text: str,
    max_chars: int = 900,
) -> List[Dict[str, Any]]:
    """
    Create chunks while preserving section provenance.
    """

    sections = _split_resume_sections(
        resume_text
    )

    chunks: List[
        Dict[str, Any]
    ] = []

    for section_data in sections:

        section = section_data[
            "section"
        ]

        text = section_data[
            "text"
        ]

        paragraphs = re.split(
            r"\n\s*\n",
            text,
        )

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if len(
                paragraph
            ) <= max_chars:

                chunks.append(
                    {
                        "text": paragraph,
                        "section": section,
                    }
                )

                continue

            sentences = re.split(
                r"(?<=[.!?])\s+|\n+",
                paragraph,
            )

            buffer = ""

            for sentence in sentences:

                sentence = sentence.strip()

                if not sentence:
                    continue

                if (
                    buffer
                    and len(buffer)
                    + len(sentence)
                    + 1
                    > max_chars
                ):

                    chunks.append(
                        {
                            "text": buffer,
                            "section": section,
                        }
                    )

                    buffer = sentence

                else:

                    if buffer:
                        buffer += " "

                    buffer += sentence

            if buffer:

                chunks.append(
                    {
                        "text": buffer,
                        "section": section,
                    }
                )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not chunks:

        text = resume_text.strip()

        for i in range(
            0,
            len(text),
            max_chars,
        ):

            chunks.append(
                {
                    "text": text[
                        i:i + max_chars
                    ],
                    "section": "GENERAL",
                }
            )

    return chunks


# ============================================================
# BUILD CURRENT RESUME FAISS INDEX
# ============================================================

def _build_resume_index(
    chunks: List[Dict[str, Any]],
) -> Tuple[Any, np.ndarray]:

    if not chunks:
        raise ValueError(
            "Cannot build resume index without chunks."
        )

    model = _load_model()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32",
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    return index, embeddings


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def _semantic_search(
    requirement: str,
    chunks: List[Dict[str, Any]],
    index: Any,
    top_k: int = 5,
) -> List[Dict[str, Any]]:

    model = _load_model()

    query_embedding = model.encode(
        [requirement],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32",
    )

    k = min(
        top_k,
        len(chunks),
    )

    scores, indices = index.search(
        query_embedding,
        k,
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0],
    ):

        if idx < 0:
            continue

        results.append(
            {
                "chunk_index": int(
                    idx
                ),
                "text": chunks[
                    idx
                ]["text"],
                "section": chunks[
                    idx
                ]["section"],
                "similarity": round(
                    float(score),
                    4,
                ),
            }
        )

    return results


# ============================================================
# EXACT PHRASE MATCH
# ============================================================

def _phrase_present(
    phrase: str,
    text: str,
) -> bool:
    """
    Check whether a requirement phrase is explicitly present in text.

    Matching rules:
        1. Never use raw substring matching.
        2. Use explicit aliases for known technologies.
        3. Use token boundaries so that:
               SQL != PostgreSQL
               C != C++
               Go != Google
        4. Allow flexible whitespace inside multi-word phrases.
    """

    phrase = _clean_text(
        phrase
    )

    text = _clean_text(
        text
    )

    if not phrase or not text:
        return False

    phrase_key = _normalize_key(
        phrase
    )

    text_key = _normalize_key(
        text
    )

    if not phrase_key or not text_key:
        return False

    aliases = {
        "go": [
            r"(?<![A-Za-z0-9_])go(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])golang(?![A-Za-z0-9_])",
        ],

        "golang": [
            r"(?<![A-Za-z0-9_])go(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])golang(?![A-Za-z0-9_])",
        ],

        "aws": [
            r"(?<![A-Za-z0-9_])aws(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])amazon\s+web\s+services(?![A-Za-z0-9_])",
        ],

        "google cloud platform": [
            r"(?<![A-Za-z0-9_])gcp(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])google\s+cloud(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])google\s+cloud\s+platform(?![A-Za-z0-9_])",
        ],

        "azure": [
            r"(?<![A-Za-z0-9_])azure(?![A-Za-z0-9_])",
        ],

        "kafka": [
            r"(?<![A-Za-z0-9_])kafka(?![A-Za-z0-9_])",
        ],

        "kinesis": [
            r"(?<![A-Za-z0-9_])kinesis(?![A-Za-z0-9_])",
        ],

        "docker": [
            r"(?<![A-Za-z0-9_])docker(?![A-Za-z0-9_])",
        ],

        "kubernetes": [
            r"(?<![A-Za-z0-9_])kubernetes(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])k8s(?![A-Za-z0-9_])",
        ],

        "python": [
            r"(?<![A-Za-z0-9_])python(?![A-Za-z0-9_])",
        ],

        "sql": [
            r"(?<![A-Za-z0-9_])sql(?![A-Za-z0-9_])",
        ],

        "rest apis": [
            r"(?<![A-Za-z0-9_])rest\s+apis?(?![A-Za-z0-9_])",
        ],

        "fastapi": [
            r"(?<![A-Za-z0-9_])fastapi(?![A-Za-z0-9_])",
        ],

        "spring boot": [
            r"(?<![A-Za-z0-9_])spring\s+boot(?![A-Za-z0-9_])",
        ],

        "prometheus": [
            r"(?<![A-Za-z0-9_])prometheus(?![A-Za-z0-9_])",
        ],

        "grafana": [
            r"(?<![A-Za-z0-9_])grafana(?![A-Za-z0-9_])",
        ],

        "opentelemetry": [
            r"(?<![A-Za-z0-9_])open\s*telemetry(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])opentelemetry(?![A-Za-z0-9_])",
        ],

        "ci/cd": [
            r"(?<![A-Za-z0-9_])ci\s*/\s*cd(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])cicd(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])continuous\s+integration(?![A-Za-z0-9_])",
            r"(?<![A-Za-z0-9_])continuous\s+deployment(?![A-Za-z0-9_])",
        ],

        "c": [
            r"(?<![A-Za-z0-9_])c(?![A-Za-z0-9_])",
        ],

        "c++": [
            r"(?<![A-Za-z0-9_])c\+\+(?![A-Za-z0-9_])",
        ],

        "c#": [
            r"(?<![A-Za-z0-9_])c#(?![A-Za-z0-9_])",
        ],
    }

    patterns = aliases.get(
        phrase_key
    )

    if patterns:
        for pattern in patterns:
            if re.search(
                pattern,
                text_key,
                flags=re.IGNORECASE,
            ):
                return True

    # --------------------------------------------------------
    # Generic exact phrase matching.
    #
    # No raw substring check.
    # --------------------------------------------------------

    escaped = re.escape(
        phrase_key
    )

    escaped = escaped.replace(
        r"\ ",
        r"\s+",
    )

    pattern = (
        rf"(?<![A-Za-z0-9_])"
        rf"{escaped}"
        rf"(?![A-Za-z0-9_])"
    )

    return bool(
        re.search(
            pattern,
            text_key,
            flags=re.IGNORECASE,
        )
    )
# ============================================================
# DIRECT EVIDENCE
# ============================================================

def _find_direct_phrase(
    requirement: str,
    chunks: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:

    for idx, chunk in enumerate(
        chunks
    ):

        if _phrase_present(
            requirement,
            chunk["text"],
        ):

            section = chunk[
                "section"
            ]

            if section in {
                "EXPERIENCE",
                "PROJECTS",
                "CERTIFICATIONS",
            }:

                confidence = (
                    LEXICAL_SECTION_CONFIDENCE
                )

                quality = "HIGH"

            elif section in {
                "SKILLS",
            }:

                confidence = (
                    LEXICAL_DIRECT_CONFIDENCE
                )

                quality = "MEDIUM"

            else:

                confidence = (
                    LEXICAL_DIRECT_CONFIDENCE
                )

                quality = "MEDIUM"

            return {
                "chunk_index": idx,
                "text": chunk["text"],
                "section": section,
                "similarity": 1.0,
                "confidence": confidence,
                "evidence_quality": quality,
            }

    return None


# ============================================================
# RELATED EVIDENCE
# ============================================================

def _find_related_phrase(
    requirement: str,
    chunks: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:

    key = _normalize_key(
        requirement
    )

    related_targets = RELATED_TERMS.get(
        key,
        set(),
    )

    if not related_targets:
        return None

    for target in related_targets:

        evidence = _find_direct_phrase(
            target,
            chunks,
        )

        if evidence:

            evidence = dict(
                evidence
            )

            evidence[
                "matched_related_term"
            ] = target

            evidence[
                "confidence"
            ] = 0.70

            evidence[
                "evidence_quality"
            ] = "LOW"

            return evidence

    return None


# ============================================================
# EDUCATION LEVEL
# ============================================================

def _detect_education_level(
    resume_text: str,
) -> Optional[str]:

    text = _normalize_key(
        resume_text
    )

    if re.search(
        r"\b(?:phd|ph\.d|doctorate|doctoral)\b",
        text,
    ):

        return "doctorate"

    if re.search(
        r"\b(?:m\.?tech|mtech|m\.?e|master(?:'s)?(?: degree)?|msc|m\.sc)\b",
        text,
    ):

        return "master"

    if re.search(
        r"\b(?:b\.?tech|btech|b\.?e|be|bachelor(?:'s)?(?: degree)?|bsc|b\.sc)\b",
        text,
    ):

        return "bachelor"

    return None


# ============================================================
# EDUCATION MATCH
# ============================================================

def _education_requirement_match(
    requirement: str,
    resume_text: str,
) -> Optional[Dict[str, Any]]:

    requirement_key = _normalize_key(
        requirement
    )

    target = None

    if (
        "bachelor" in requirement_key
        or "b.tech" in requirement_key
        or "btech" in requirement_key
    ):

        target = "bachelor"

    elif (
        "master" in requirement_key
        or "m.tech" in requirement_key
        or "mtech" in requirement_key
    ):

        target = "master"

    elif (
        "phd" in requirement_key
        or "doctorate" in requirement_key
    ):

        target = "doctorate"

    if not target:
        return None

    actual = _detect_education_level(
        resume_text
    )

    if not actual:

        return {
            "status": MISSING,
            "resume_proof": None,
            "source_section": None,
            "evidence_quality": "NONE",
            "education_match": "MISSING",
            "confidence": 0.0,
            "similarity": 0.0,
            "matched_chunk_index": None,
        }

    hierarchy = {
        "bachelor": 1,
        "master": 2,
        "doctorate": 3,
    }

    if (
        hierarchy.get(
            actual,
            0,
        )
        >= hierarchy.get(
            target,
            0,
        )
    ):

        proof_patterns = {
            "bachelor": (
                r"(?:b\.?\s*tech|btech|b\.?\s*e|"
                r"bachelor(?:'s)?(?: degree)?)"
            ),

            "master": (
                r"(?:m\.?\s*tech|mtech|m\.?\s*e|"
                r"master(?:'s)?(?: degree)?)"
            ),

            "doctorate": (
                r"(?:ph\.?\s*d|doctorate|doctoral)"
            ),
        }

        pattern = proof_patterns[
            actual
        ]

        match = re.search(
            pattern,
            resume_text,
            flags=re.IGNORECASE,
        )

        if match:

            start = max(
                0,
                match.start() - 80,
            )

            end = min(
                len(resume_text),
                match.end() + 120,
            )

            proof = resume_text[
                start:end
            ].strip()

        else:

            proof = actual

        return {
            "status": DIRECT,
            "resume_proof": proof,
            "source_section": "EDUCATION",
            "evidence_quality": "HIGH",
            "education_match": (
                "EXACT"
                if actual == target
                else "EQUIVALENT"
            ),
            "confidence": 0.95,
            "similarity": 1.0,
            "matched_chunk_index": None,
        }

    return {
        "status": MISSING,
        "resume_proof": None,
        "source_section": None,
        "evidence_quality": "NONE",
        "education_match": "INSUFFICIENT",
        "confidence": 0.0,
        "similarity": 0.0,
        "matched_chunk_index": None,
    }


# ============================================================
# EXPERIENCE YEARS
# ============================================================

def _extract_resume_experience_years(
    resume_text: str,
) -> Optional[float]:

    # --------------------------------------------------------
    # Explicit experience statements
    # --------------------------------------------------------

    patterns = [
        (
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?"
            r"\s+(?:of\s+)?"
            r"(?:professional\s+)?experience"
        ),

        (
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?"
            r"\s+backend\s+experience"
        ),

        (
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?"
            r"\s+software\s+engineering\s+experience"
        ),
    ]

    values = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            resume_text,
            flags=re.IGNORECASE,
        ):

            try:

                values.append(
                    float(
                        match.group(1)
                    )
                )

            except Exception:
                pass

    if values:
        return max(values)

    # --------------------------------------------------------
    # Date-range fallback
    # --------------------------------------------------------

    month_map = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }

    current_year = 2026
    current_month = 9

    date_pattern = re.compile(
        r"("
        r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
        r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
        r"aug(?:ust)?|sep(?:t(?:ember)?)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"\s+\d{4}"
        r")"
        r"\s*(?:-|–|—|to)\s*"
        r"("
        r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
        r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
        r"aug(?:ust)?|sep(?:t(?:ember)?)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"\s+\d{4}"
        r"|present|current"
        r")",
        flags=re.IGNORECASE,
    )

    ranges = []

    for match in date_pattern.finditer(
        resume_text
    ):

        start_text = (
            match.group(1)
            .lower()
        )

        end_text = (
            match.group(2)
            .lower()
        )

        start_match = re.match(
            r"([a-z]+)\s+(\d{4})",
            start_text,
        )

        if not start_match:
            continue

        start_month = month_map.get(
            start_match.group(1)
        )

        start_year = int(
            start_match.group(2)
        )

        if not start_month:
            continue

        if end_text in {
            "present",
            "current",
        }:

            end_year = current_year
            end_month = current_month

        else:

            end_match = re.match(
                r"([a-z]+)\s+(\d{4})",
                end_text,
            )

            if not end_match:
                continue

            end_month = month_map.get(
                end_match.group(1)
            )

            end_year = int(
                end_match.group(2)
            )

        if not end_month:
            continue

        if (
            end_year < start_year
            or (
                end_year == start_year
                and end_month < start_month
            )
        ):
            continue

        months = (
            end_year * 12
            + end_month
            - (
                start_year * 12
                + start_month
            )
        )

        years = months / 12.0

        if years >= 0:
            ranges.append(
                years
            )

    if ranges:

        # Conservative implementation:
        # use the longest continuous date range.
        return round(
            max(ranges),
            2,
        )

    return None


# ============================================================
# EXPERIENCE EVIDENCE
# ============================================================

def _experience_evidence(
    requirement: Dict[str, Any],
    resume_text: str,
    chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:

    required_years = requirement.get(
        "required_years"
    )

    if required_years is None:

        evidence = _clean_text(
            requirement.get(
                "evidence",
                "",
            )
        )

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            evidence,
            flags=re.IGNORECASE,
        )

        if match:

            try:

                required_years = float(
                    match.group(1)
                )

            except Exception:
                pass

    resume_years = (
        _extract_resume_experience_years(
            resume_text
        )
    )

    if required_years is None:

        direct = _find_direct_phrase(
            requirement.get(
                "requirement",
                "",
            ),
            chunks,
        )

        if direct:

            return {
                "status": DIRECT,
                "resume_proof": direct[
                    "text"
                ],
                "source_section": direct[
                    "section"
                ],
                "evidence_quality": direct[
                    "evidence_quality"
                ],
                "resume_experience_years": resume_years,
                "required_experience_years": None,
                "confidence": direct[
                    "confidence"
                ],
                "similarity": direct[
                    "similarity"
                ],
                "matched_chunk_index": direct[
                    "chunk_index"
                ],
            }

        return {
            "status": UNKNOWN,
            "resume_proof": None,
            "source_section": None,
            "evidence_quality": "NONE",
            "resume_experience_years": resume_years,
            "required_experience_years": None,
            "confidence": 0.0,
            "similarity": 0.0,
            "matched_chunk_index": None,
        }

    if resume_years is None:

        return {
            "status": UNKNOWN,
            "resume_proof": None,
            "source_section": None,
            "evidence_quality": "NONE",
            "resume_experience_years": None,
            "required_experience_years": required_years,
            "confidence": 0.0,
            "similarity": 0.0,
            "matched_chunk_index": None,
        }

    # --------------------------------------------------------
    # Experience satisfied
    # --------------------------------------------------------

    if resume_years >= required_years:

        experience_chunks = [
            (
                i,
                chunk,
            )
            for i, chunk in enumerate(
                chunks
            )
            if chunk["section"]
            == "EXPERIENCE"
        ]

        proof = None
        proof_index = None
        proof_section = None

        if experience_chunks:

            proof_index, proof_chunk = max(
                experience_chunks,
                key=lambda pair: len(
                    pair[1]["text"]
                ),
            )

            proof = proof_chunk[
                "text"
            ]

            proof_section = (
                proof_chunk[
                    "section"
                ]
            )

        else:

            summary_chunks = [
                (
                    i,
                    chunk,
                )
                for i, chunk in enumerate(
                    chunks
                )
                if chunk["section"]
                == "SUMMARY"
            ]

            if summary_chunks:

                proof_index, proof_chunk = max(
                    summary_chunks,
                    key=lambda pair: len(
                        pair[1]["text"]
                    ),
                )

                proof = proof_chunk[
                    "text"
                ]

                proof_section = (
                    proof_chunk[
                        "section"
                    ]
                )

        return {
            "status": DIRECT,
            "resume_proof": proof,
            "source_section": proof_section,
            "evidence_quality": (
                "HIGH"
                if proof_section
                == "EXPERIENCE"
                else "MEDIUM"
            ),
            "resume_experience_years": resume_years,
            "required_experience_years": required_years,
            "confidence": 0.95,
            "similarity": 1.0,
            "matched_chunk_index": proof_index,
        }

    # --------------------------------------------------------
    # Experience insufficient
    # --------------------------------------------------------

    return {
        "status": PARTIAL,
        "resume_proof": (
            f"Documented experience: "
            f"{resume_years:.2f} years"
        ),
        "source_section": "EXPERIENCE",
        "evidence_quality": "HIGH",
        "resume_experience_years": resume_years,
        "required_experience_years": required_years,
        "confidence": 0.95,
        "similarity": 1.0,
        "matched_chunk_index": None,
    }


# ============================================================
# SINGLE REQUIREMENT
# ============================================================

def analyze_requirement(
    requirement: Dict[str, Any],
    resume_text: str,
    chunks: Optional[
        List[Dict[str, Any]]
    ] = None,
    index: Any = None,
    top_k: int = 5,
) -> Dict[str, Any]:

    if chunks is None:

        chunks = _split_into_chunks(
            resume_text
        )

    if index is None:

        index, _ = _build_resume_index(
            chunks
        )

    raw_name = (
        requirement.get(
            "requirement"
        )
        or requirement.get(
            "skill"
        )
        or requirement.get(
            "name"
        )
        or ""
    )

    name = _normalize_requirement_name(
        raw_name
    )

    requirement_type = _clean_text(
        requirement.get(
            "type",
            "UNKNOWN",
        )
    ).upper()

    logic = _normalize_logic(
        requirement.get(
            "logic",
            SINGLE,
        )
    )

    # ========================================================
    # LOGICAL GROUP
    # ========================================================

    if logic in {
        ANY_OF,
        ALL_OF,
    }:

        return analyze_requirement_group(
            requirement=requirement,
            resume_text=resume_text,
            chunks=chunks,
            index=index,
            top_k=top_k,
        )

    # ========================================================
    # EDUCATION
    # ========================================================

    if requirement_type == "EDUCATION":

        education_result = (
            _education_requirement_match(
                name,
                resume_text,
            )
        )

        if education_result is not None:

            return {
                "requirement": name,
                "importance": requirement.get(
                    "importance",
                    "UNKNOWN",
                ),
                "type": requirement_type,
                "logic": SINGLE,
                "options": [],
                **education_result,
            }

    # ========================================================
    # EXPERIENCE
    # ========================================================

    if requirement_type == "EXPERIENCE":

        result = _experience_evidence(
            requirement,
            resume_text,
            chunks,
        )

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement_type,
            "logic": SINGLE,
            "options": [],
            **result,
        }

    # ========================================================
    # DIRECT MATCH
    # ========================================================

    direct = _find_direct_phrase(
        name,
        chunks,
    )

    if direct:

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement_type,
            "logic": SINGLE,
            "options": [],
            "status": DIRECT,
            "resume_proof": direct[
                "text"
            ],
            "source_section": direct[
                "section"
            ],
            "evidence_quality": direct[
                "evidence_quality"
            ],
            "confidence": direct[
                "confidence"
            ],
            "similarity": direct[
                "similarity"
            ],
            "matched_chunk_index": direct[
                "chunk_index"
            ],
        }

    # ========================================================
    # RELATED MATCH
    # ========================================================

    related = _find_related_phrase(
        name,
        chunks,
    )

    if related:

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement_type,
            "logic": SINGLE,
            "options": [],
            "status": RELATED,
            "resume_proof": related[
                "text"
            ],
            "source_section": related[
                "section"
            ],
            "evidence_quality": related[
                "evidence_quality"
            ],
            "confidence": related[
                "confidence"
            ],
            "similarity": related[
                "similarity"
            ],
            "matched_chunk_index": related[
                "chunk_index"
            ],
            "matched_related_term": related.get(
                "matched_related_term"
            ),
        }

    # ========================================================
    # SEMANTIC MATCH
    # ========================================================

    semantic_results = _semantic_search(
        name,
        chunks,
        index,
        top_k=top_k,
    )

    best = (
        semantic_results[0]
        if semantic_results
        else None
    )

    if best is None:

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement_type,
            "logic": SINGLE,
            "options": [],
            "status": MISSING,
            "resume_proof": None,
            "source_section": None,
            "evidence_quality": "NONE",
            "confidence": 0.0,
            "similarity": 0.0,
            "matched_chunk_index": None,
        }

    similarity = best[
        "similarity"
    ]

    # --------------------------------------------------------
    # Important:
    # semantic similarity alone does NOT produce DIRECT.
    # --------------------------------------------------------

    if similarity >= DIRECT_SIMILARITY:

        status = RELATED
        confidence = min(
            0.82,
            similarity,
        )

    elif similarity >= RELATED_SIMILARITY:

        status = RELATED
        confidence = min(
            0.68,
            similarity,
        )

    elif similarity >= PARTIAL_SIMILARITY:

        status = PARTIAL
        confidence = min(
            0.50,
            similarity,
        )

    else:

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement_type,
            "logic": SINGLE,
            "options": [],
            "status": MISSING,
            "resume_proof": None,
            "source_section": None,
            "evidence_quality": "NONE",
            "confidence": 0.0,
            "similarity": similarity,
            "matched_chunk_index": None,
        }

    return {
        "requirement": name,
        "importance": requirement.get(
            "importance",
            "UNKNOWN",
        ),
        "type": requirement_type,
        "logic": SINGLE,
        "options": [],
        "status": status,
        "resume_proof": best[
            "text"
        ],
        "source_section": best[
            "section"
        ],
        "evidence_quality": "LOW",
        "confidence": round(
            confidence,
            4,
        ),
        "similarity": similarity,
        "matched_chunk_index": best[
            "chunk_index"
        ],
    }


# ============================================================
# ANALYZE ONE OPTION
# ============================================================

def _analyze_option(
    option: str,
    parent_requirement: Dict[str, Any],
    resume_text: str,
    chunks: List[Dict[str, Any]],
    index: Any,
    top_k: int,
) -> Dict[str, Any]:
    """
    Evaluate one concrete option independently.

    Example:

        Cloud provider
        options = [AWS, GCP, Azure]

    becomes:

        AWS
        GCP
        Azure

    evaluated independently.
    """

    option_requirement = {
        "requirement": option,
        "importance": parent_requirement.get(
            "importance",
            "UNKNOWN",
        ),
        "type": parent_requirement.get(
            "type",
            "SKILL",
        ),
        "logic": SINGLE,
        "options": [],
        "evidence": parent_requirement.get(
            "evidence"
        ),
    }

    result = analyze_requirement(
        requirement=option_requirement,
        resume_text=resume_text,
        chunks=chunks,
        index=index,
        top_k=top_k,
    )

    result = dict(
        result
    )

    result[
        "option"
    ] = option

    return result


# ============================================================
# STATUS RANK
# ============================================================

def _status_rank(
    status: str,
) -> int:

    return {
        DIRECT: 5,
        RELATED: 4,
        PARTIAL: 3,
        UNKNOWN: 2,
        MISSING: 1,
    }.get(
        status,
        0,
    )


# ============================================================
# BEST EVIDENCE
# ============================================================

def _best_evidence(
    results: List[
        Dict[str, Any]
    ],
) -> Optional[
    Dict[str, Any]
]:

    if not results:
        return None

    return max(
        results,
        key=lambda result: (
            _status_rank(
                result.get(
                    "status",
                    UNKNOWN,
                )
            ),

            float(
                result.get(
                    "confidence",
                    0.0,
                )
            ),

            float(
                result.get(
                    "similarity",
                    0.0,
                )
            ),
        ),
    )


# ============================================================
# LOGICAL GROUP
# ============================================================

def analyze_requirement_group(
    requirement: Dict[str, Any],
    resume_text: str,
    chunks: List[Dict[str, Any]],
    index: Any,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Evaluate ANY_OF / ALL_OF requirements.

    ANY_OF:
        At least one option needs evidence.

    ALL_OF:
        Every option needs evidence.
    """

    name = _normalize_requirement_name(
        requirement.get(
            "requirement",
            "",
        )
    )

    logic = _normalize_logic(
        requirement.get(
            "logic",
            SINGLE,
        )
    )

    raw_options = requirement.get(
        "options",
        [],
    )

    if not isinstance(
        raw_options,
        list,
    ):

        raw_options = []

    options = []

    for option in raw_options:

        option = _normalize_requirement_name(
            option
        )

        if option and option not in options:

            options.append(
                option
            )

    # --------------------------------------------------------
    # No options -> SINGLE
    # --------------------------------------------------------

    if not options:

        single_requirement = dict(
            requirement
        )

        single_requirement[
            "logic"
        ] = SINGLE

        return analyze_requirement(
            requirement=single_requirement,
            resume_text=resume_text,
            chunks=chunks,
            index=index,
            top_k=top_k,
        )

    # --------------------------------------------------------
    # Evaluate every option independently.
    # --------------------------------------------------------

    option_results = []

    for option in options:

        result = _analyze_option(
            option=option,
            parent_requirement=requirement,
            resume_text=resume_text,
            chunks=chunks,
            index=index,
            top_k=top_k,
        )

        option_results.append(
            result
        )

    # ========================================================
    # ANY_OF
    # ========================================================

    if logic == ANY_OF:

        direct_results = [
            result
            for result in option_results
            if result.get(
                "status"
            ) == DIRECT
        ]

        related_results = [
            result
            for result in option_results
            if result.get(
                "status"
            ) == RELATED
        ]

        partial_results = [
            result
            for result in option_results
            if result.get(
                "status"
            ) == PARTIAL
        ]

        # --------------------------------------------
        # Direct option wins.
        # --------------------------------------------

        if direct_results:

            matched = _best_evidence(
                direct_results
            )

            status = DIRECT

        # --------------------------------------------
        # Related option.
        # --------------------------------------------

        elif related_results:

            matched = _best_evidence(
                related_results
            )

            status = RELATED

        # --------------------------------------------
        # Partial option.
        # --------------------------------------------

        elif partial_results:

            matched = _best_evidence(
                partial_results
            )

            status = PARTIAL

        # --------------------------------------------
        # Nothing found.
        # --------------------------------------------

        else:

            matched = _best_evidence(
                option_results
            )

            status = (
                UNKNOWN
                if any(
                    result.get(
                        "status"
                    ) == UNKNOWN
                    for result
                    in option_results
                )
                else MISSING
            )

        if matched is None:

            return {
                "requirement": name,
                "importance": requirement.get(
                    "importance",
                    "UNKNOWN",
                ),
                "type": requirement.get(
                    "type",
                    "UNKNOWN",
                ),
                "logic": ANY_OF,
                "options": options,
                "status": MISSING,
                "resume_proof": None,
                "source_section": None,
                "evidence_quality": "NONE",
                "confidence": 0.0,
                "similarity": 0.0,
                "matched_chunk_index": None,
                "matched_option": None,
                "option_results": option_results,
            }

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement.get(
                "type",
                "UNKNOWN",
            ),
            "logic": ANY_OF,
            "options": options,
            "status": status,
            "resume_proof": (
                matched.get(
                    "resume_proof"
                )
                if status
                != MISSING
                else None
            ),
            "source_section": (
                matched.get(
                    "source_section"
                )
                if status
                != MISSING
                else None
            ),
            "evidence_quality": (
                matched.get(
                    "evidence_quality",
                    "NONE",
                )
                if status
                != MISSING
                else "NONE"
            ),
            "confidence": (
                matched.get(
                    "confidence",
                    0.0,
                )
                if status
                != MISSING
                else 0.0
            ),
            "similarity": matched.get(
                "similarity",
                0.0,
            ),
            "matched_chunk_index": (
                matched.get(
                    "matched_chunk_index"
                )
                if status
                != MISSING
                else None
            ),
            "matched_option": (
                matched.get(
                    "option"
                )
                if status
                != MISSING
                else None
            ),
            "option_results": option_results,
        }

    # ========================================================
    # ALL_OF
    # ========================================================

    if logic == ALL_OF:

        direct_count = sum(
            1
            for result in option_results
            if result.get(
                "status"
            ) == DIRECT
        )

        related_count = sum(
            1
            for result in option_results
            if result.get(
                "status"
            ) == RELATED
        )

        partial_count = sum(
            1
            for result in option_results
            if result.get(
                "status"
            ) == PARTIAL
        )

        missing_count = sum(
            1
            for result in option_results
            if result.get(
                "status"
            ) == MISSING
        )

        unknown_count = sum(
            1
            for result in option_results
            if result.get(
                "status"
            ) == UNKNOWN
        )

        total = len(
            option_results
        )

        # --------------------------------------------
        # All options directly evidenced.
        # --------------------------------------------

        if (
            direct_count == total
        ):

            status = DIRECT

        # --------------------------------------------
        # All options have evidence but not all direct.
        # --------------------------------------------

        elif (
            missing_count == 0
            and unknown_count == 0
            and (
                direct_count
                + related_count
                == total
            )
        ):

            status = RELATED

        # --------------------------------------------
        # Some evidence but incomplete.
        # --------------------------------------------

        elif (
            direct_count
            + related_count
            + partial_count
            > 0
        ):

            status = PARTIAL

        # --------------------------------------------
        # Nothing found.
        # --------------------------------------------

        elif (
            missing_count == total
        ):

            status = MISSING

        else:

            status = UNKNOWN

        # Representative evidence.
        best = _best_evidence(
            option_results
        )

        if total:

            confidence = round(
                sum(
                    float(
                        result.get(
                            "confidence",
                            0.0,
                        )
                    )
                    for result
                    in option_results
                )
                / total,
                4,
            )

            similarity = round(
                sum(
                    float(
                        result.get(
                            "similarity",
                            0.0,
                        )
                    )
                    for result
                    in option_results
                )
                / total,
                4,
            )

        else:

            confidence = 0.0
            similarity = 0.0

        return {
            "requirement": name,
            "importance": requirement.get(
                "importance",
                "UNKNOWN",
            ),
            "type": requirement.get(
                "type",
                "UNKNOWN",
            ),
            "logic": ALL_OF,
            "options": options,
            "status": status,
            "resume_proof": (
                best.get(
                    "resume_proof"
                )
                if best
                else None
            ),
            "source_section": (
                best.get(
                    "source_section"
                )
                if best
                else None
            ),
            "evidence_quality": (
                "HIGH"
                if status == DIRECT
                else "MEDIUM"
                if status == RELATED
                else "LOW"
                if status == PARTIAL
                else "NONE"
            ),
            "confidence": confidence,
            "similarity": similarity,
            "matched_chunk_index": (
                best.get(
                    "matched_chunk_index"
                )
                if best
                else None
            ),
            "matched_option": None,
            "option_results": option_results,
            "satisfied_options": [
                result.get(
                    "option"
                )
                for result in option_results
                if result.get(
                    "status"
                ) == DIRECT
            ],
            "missing_options": [
                result.get(
                    "option"
                )
                for result in option_results
                if result.get(
                    "status"
                ) in {
                    MISSING,
                    UNKNOWN,
                }
            ],
        }

    # ========================================================
    # FALLBACK
    # ========================================================

    return analyze_requirement(
        requirement={
            **requirement,
            "logic": SINGLE,
        },
        resume_text=resume_text,
        chunks=chunks,
        index=index,
        top_k=top_k,
    )


# ============================================================
# PREPARE REQUIREMENT
# ============================================================

def _prepare_requirement(
    requirement: Dict[str, Any],
) -> Dict[str, Any]:

    result = dict(
        requirement
    )

    name = (
        result.get(
            "requirement"
        )
        or result.get(
            "skill"
        )
        or result.get(
            "name"
        )
        or ""
    )

    result[
        "requirement"
    ] = _normalize_requirement_name(
        name
    )

    # IMPORTANT:
    # This now correctly preserves ANY_OF / ALL_OF.
    result[
        "logic"
    ] = _normalize_logic(
        result.get(
            "logic",
            SINGLE,
        )
    )

    raw_options = result.get(
        "options",
        [],
    )

    if not isinstance(
        raw_options,
        list,
    ):

        raw_options = []

    normalized_options = []

    for option in raw_options:

        option = _normalize_requirement_name(
            option
        )

        if (
            option
            and option not in normalized_options
        ):

            normalized_options.append(
                option
            )

    result[
        "options"
    ] = normalized_options

    result[
        "importance"
    ] = _clean_text(
        result.get(
            "importance",
            "UNKNOWN",
        )
    ).upper()

    result[
        "type"
    ] = _clean_text(
        result.get(
            "type",
            "UNKNOWN",
        )
    ).upper()

    # --------------------------------------------------------
    # Experience requirement
    # --------------------------------------------------------

    if (
        result.get(
            "type"
        )
        == "EXPERIENCE"
    ):

        evidence = _clean_text(
            result.get(
                "evidence",
                "",
            )
        )

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            evidence,
            flags=re.IGNORECASE,
        )

        if match:

            try:

                result[
                    "required_years"
                ] = float(
                    match.group(1)
                )

            except Exception:
                pass

    return result


# ============================================================
# ANALYZE REQUIREMENTS
# ============================================================

def analyze_requirements(
    job_requirements: List[
        Dict[str, Any]
    ],
    resume_text: str,
    top_k: int = 5,
) -> List[
    Dict[str, Any]
]:

    # IMPORTANT:
    # Preserve newlines.
    resume_text = (
        _preserve_resume_text(
            resume_text
        )
    )

    if not resume_text:
        return []

    chunks = _split_into_chunks(
        resume_text
    )

    if not chunks:
        return []

    index, _ = _build_resume_index(
        chunks
    )

    results = []

    for raw_requirement in job_requirements:

        if not isinstance(
            raw_requirement,
            dict,
        ):

            continue

        requirement = (
            _prepare_requirement(
                raw_requirement
            )
        )

        result = analyze_requirement(
            requirement=requirement,
            resume_text=resume_text,
            chunks=chunks,
            index=index,
            top_k=top_k,
        )

        results.append(
            result
        )

    return results


# ============================================================
# ANALYZE COMPLETE JOB
# ============================================================

def analyze_job(
    job_requirements: Dict[str, Any],
    resume_text: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Analyze one complete job against one current resume.

    Does NOT make the final APPLY / IMPROVE / DON'T PRIORITIZE
    decision.
    """

    # IMPORTANT FIX:
    # Never collapse resume newlines here.
    resume_text = (
        _preserve_resume_text(
            resume_text
        )
    )

    if not resume_text:

        raise ValueError(
            "resume_text cannot be empty"
        )

    if not isinstance(
        job_requirements,
        dict,
    ):

        raise TypeError(
            "job_requirements must be a dictionary"
        )

    requirements = (
        job_requirements.get(
            "requirements",
            [],
        )
    )

    if not isinstance(
        requirements,
        list,
    ):

        requirements = []

    # ========================================================
    # TOP-LEVEL EXPERIENCE
    # ========================================================

    experience_data = (
        job_requirements.get(
            "experience",
            {},
        )
    )

    if (
        isinstance(
            experience_data,
            dict,
        )
        and experience_data.get(
            "minimum_years"
        )
        is not None
    ):

        has_experience = any(
            isinstance(
                item,
                dict,
            )
            and (
                str(
                    item.get(
                        "type",
                        "",
                    )
                ).upper()
                == "EXPERIENCE"
            )
            for item in requirements
        )

        if not has_experience:

            requirements = list(
                requirements
            )

            requirements.append(
                {
                    "requirement": (
                        "Professional experience"
                    ),
                    "importance": "REQUIRED",
                    "type": "EXPERIENCE",
                    "logic": SINGLE,
                    "options": [],
                    "evidence": (
                        experience_data.get(
                            "evidence"
                        )
                    ),
                    "required_years": (
                        experience_data.get(
                            "minimum_years"
                        )
                    ),
                }
            )

    # ========================================================
    # EVIDENCE ANALYSIS
    # ========================================================

    evidence_breakdown = (
        analyze_requirements(
            job_requirements=requirements,
            resume_text=resume_text,
            top_k=top_k,
        )
    )

    # ========================================================
    # RESUME SUMMARY
    # ========================================================

    resume_years = (
        _extract_resume_experience_years(
            resume_text
        )
    )

    education_level = (
        _detect_education_level(
            resume_text
        )
    )

    return {
        "role": job_requirements.get(
            "role"
        ),

        "experience": {
            "minimum_years": (
                experience_data.get(
                    "minimum_years"
                )
                if isinstance(
                    experience_data,
                    dict,
                )
                else None
            ),

            "evidence": (
                experience_data.get(
                    "evidence"
                )
                if isinstance(
                    experience_data,
                    dict,
                )
                else None
            ),
        },

        "resume_summary": {
            "documented_experience_years": (
                resume_years
            ),
            "education_level": (
                education_level
            ),
        },

        "evidence_breakdown": (
            evidence_breakdown
        ),
    }


# ============================================================
# TEST RESUME
# ============================================================

def _test_resume() -> str:

    return """
SUMMARY

Backend developer with 3 years of experience building APIs
and distributed backend services.

SKILLS

Go, Python, Docker, AWS, SQL

EXPERIENCE

Backend Developer
2023 - Present

Built and maintained backend services using Go and Python.
Designed REST APIs and worked with SQL databases.
Deployed applications using Docker.

PROJECTS

Distributed Data Pipeline

Built a distributed backend service using Go, Kafka,
Docker and Kubernetes. Deployed the service on AWS.
Worked with high-throughput data ingestion.

EDUCATION

B.Tech in Computer Science Engineering
"""


# ============================================================
# TEST REQUIREMENTS
# ============================================================

def _test_requirements() -> Dict[str, Any]:

    return {
        "role": "Backend Developer",

        "experience": {
            "minimum_years": 2,
            "evidence": (
                "2+ years of backend experience"
            ),
        },

        "requirements": [

            # --------------------------------------------
            # ANY_OF
            # --------------------------------------------

            {
                "requirement": "Go or Rust",
                "importance": "REQUIRED",
                "type": "SKILL",
                "logic": "ANY_OF",
                "options": [
                    "Go",
                    "Rust",
                ],
                "evidence": (
                    "Go and/or Rust"
                ),
            },

            {
                "requirement": "Cloud provider",
                "importance": "REQUIRED",
                "type": "SKILL",
                "logic": "ANY_OF",
                "options": [
                    "AWS",
                    "Google Cloud Platform",
                    "Azure",
                ],
                "evidence": (
                    "At least one major cloud provider"
                ),
            },

            {
                "requirement": "Event streaming",
                "importance": "REQUIRED",
                "type": "SKILL",
                "logic": "ANY_OF",
                "options": [
                    "Kafka",
                    "Kinesis",
                ],
                "evidence": (
                    "Kafka, Kinesis, or equivalent"
                ),
            },

            # --------------------------------------------
            # ALL_OF
            # --------------------------------------------

            {
                "requirement": (
                    "Docker and Kubernetes"
                ),
                "importance": "REQUIRED",
                "type": "SKILL",
                "logic": "ALL_OF",
                "options": [
                    "Docker",
                    "Kubernetes",
                ],
                "evidence": (
                    "Docker and Kubernetes"
                ),
            },

            # --------------------------------------------
            # SINGLE
            # --------------------------------------------

            {
                "requirement": "SQL",
                "importance": "REQUIRED",
                "type": "SKILL",
                "logic": "SINGLE",
                "options": [],
                "evidence": "SQL",
            },
        ],
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    result = analyze_job(
        job_requirements=(
            _test_requirements()
        ),
        resume_text=_test_resume(),
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )