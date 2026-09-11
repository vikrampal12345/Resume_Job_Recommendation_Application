"""
Normalized requirement extraction adapter.

This module intentionally contains NO independent extraction engine.

Single source of truth:
    app.requirement_extractor

Responsibilities here:
    1. Call the main requirement extractor.
    2. Normalize/validate the returned schema.
    3. Preserve requirement semantics, evidence, and provenance.
    4. Provide a stable API for downstream components such as
       the Evidence Engine.

The extractor remains responsible for:
    - requirement discovery
    - importance classification
    - ANY_OF / ALL_OF logic
    - semantic grouping
    - deterministic fallback
    - role extraction
    - experience extraction
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .requirement_extractor import (
    extract_requirements as _extract_requirements,
)


VALID_IMPORTANCE = {
    "REQUIRED",
    "PREFERRED",
    "NICE_TO_HAVE",
    "UNKNOWN",
}

VALID_TYPES = {
    "SKILL",
    "CAPABILITY",
    "EDUCATION",
    "EXPERIENCE",
    "CONSTRAINT",
    "UNKNOWN",
}

VALID_LOGIC = {
    "SINGLE",
    "ANY_OF",
    "ALL_OF",
}


def _clean_text(value: Any) -> Optional[str]:
    """
    Convert a value to normalized text.

    Empty values become None.
    """

    if value is None:
        return None

    text = " ".join(
        str(value).split()
    ).strip()

    return text or None


def _normalize_importance(value: Any) -> str:
    """
    Normalize requirement importance without changing semantics.
    """

    value = _clean_text(value)

    if not value:
        return "UNKNOWN"

    value = value.upper()

    if value in VALID_IMPORTANCE:
        return value

    return "UNKNOWN"


def _normalize_type(value: Any) -> str:
    """
    Normalize requirement type without inventing a new type.
    """

    value = _clean_text(value)

    if not value:
        return "UNKNOWN"

    value = value.upper()

    if value in VALID_TYPES:
        return value

    return "UNKNOWN"


def _normalize_logic(value: Any) -> str:
    """
    Normalize logical relationship.
    """

    value = _clean_text(value)

    if not value:
        return "SINGLE"

    value = value.upper()

    if value in VALID_LOGIC:
        return value

    return "SINGLE"


def _normalize_options(
    options: Any,
) -> List[str]:
    """
    Normalize options while preserving their actual values.

    No new options are invented here.
    """

    if not isinstance(
        options,
        list,
    ):
        return []

    normalized: List[str] = []
    seen = set()

    for option in options:

        option_text = _clean_text(
            option
        )

        if not option_text:
            continue

        if option_text.casefold() == "equivalent":
            continue

        key = option_text.casefold()

        if key in seen:
            continue

        seen.add(key)
        normalized.append(
            option_text
        )

    return normalized


def _normalize_requirement_item(
    raw_item: Any,
) -> Optional[Dict[str, Any]]:
    """
    Normalize one requirement item.

    This function does NOT infer:
        - importance
        - requirement type
        - logical relationships
        - semantic families

    Those decisions belong to requirement_extractor.py.
    """

    if not isinstance(
        raw_item,
        dict,
    ):
        return None

    requirement = _clean_text(
        raw_item.get(
            "requirement"
        )
    )

    if not requirement:
        return None

    importance = _normalize_importance(
        raw_item.get(
            "importance"
        )
    )

    requirement_type = _normalize_type(
        raw_item.get(
            "type"
        )
    )

    logic = _normalize_logic(
        raw_item.get(
            "logic"
        )
    )

    options = _normalize_options(
        raw_item.get(
            "options",
            [],
        )
    )

    evidence = _clean_text(
        raw_item.get(
            "evidence"
        )
    )

    source = _clean_text(
        raw_item.get(
            "source"
        )
    )

    if not source:
        source = "unknown"

    # ANY_OF / ALL_OF requires at least two options.
    if logic in {
        "ANY_OF",
        "ALL_OF",
    } and len(options) < 2:
        logic = "SINGLE"

    return {
        "requirement": requirement,
        "importance": importance,
        "type": requirement_type,
        "logic": logic,
        "options": options,
        "evidence": evidence,
        "source": source,
    }


def _requirement_identity(
    item: Dict[str, Any],
) -> tuple:
    """
    Stable identity for deduplication.

    Include logical structure and options so that a genuine group
    is not accidentally collapsed into an unrelated requirement.
    """

    requirement = (
        _clean_text(
            item.get(
                "requirement"
            )
        )
        or ""
    ).casefold()

    logic = _normalize_logic(
        item.get(
            "logic"
        )
    )

    options = tuple(
        sorted(
            option.casefold()
            for option in item.get(
                "options",
                []
            )
            if _clean_text(option)
        )
    )

    return (
        requirement,
        logic,
        options,
    )


def normalize_extraction_result(
    result: Any,
) -> Dict[str, Any]:
    """
    Normalize the output of requirement_extractor.py.

    This adapter does not perform extraction itself.
    """

    if not isinstance(
        result,
        dict,
    ):
        result = {}

    role = _clean_text(
        result.get(
            "role"
        )
    )

    raw_requirements = result.get(
        "requirements",
        [],
    )

    if not isinstance(
        raw_requirements,
        list,
    ):
        raw_requirements = []

    requirements: List[Dict[str, Any]] = []
    seen = set()

    for raw_item in raw_requirements:

        item = _normalize_requirement_item(
            raw_item
        )

        if item is None:
            continue

        key = _requirement_identity(
            item
        )

        if key in seen:
            continue

        seen.add(key)
        requirements.append(
            item
        )

    raw_experience = result.get(
        "experience"
    )

    if not isinstance(
        raw_experience,
        dict,
    ):
        raw_experience = {}

    minimum_years = raw_experience.get(
        "minimum_years"
    )

    try:
        minimum_years = (
            float(minimum_years)
            if minimum_years is not None
            else None
        )
    except (
        TypeError,
        ValueError,
    ):
        minimum_years = None

    experience = {
        "minimum_years": minimum_years,
        "evidence": _clean_text(
            raw_experience.get(
                "evidence"
            )
        ),
    }

    return {
        "role": role,
        "requirements": requirements,
        "experience": experience,
    }


def extract_requirements(
    job_description: str,
    use_llm: bool = True,
) -> Dict[str, Any]:
    """
    Compatibility entry point.

    Delegates all extraction to the single source of truth and
    normalizes the resulting schema.
    """

    raw_result = _extract_requirements(
        job_description,
        use_llm=use_llm,
    )

    return normalize_extraction_result(
        raw_result
    )


# Explicit name for downstream code.
extract_requirements_normalized = (
    extract_requirements
)