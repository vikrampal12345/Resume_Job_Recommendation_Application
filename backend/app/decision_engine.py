"""
Decision Engine for Syncronal.

Purpose:

    Evidence Engine
          ↓
    Requirement-level evidence
          ↓
    Decision Engine
          ↓
    APPLY_NOW
    IMPROVE_FIRST
    DON'T_PRIORITIZE

Important:

- This engine does NOT predict hiring probability.
- It does NOT claim the candidate is definitely qualified.
- It makes a recommendation based on documented resume evidence.
- REQUIRED requirements have much higher decision impact
  than PREFERRED / NICE_TO_HAVE requirements.
"""

from __future__ import annotations

from typing import Any, Dict, List


# ============================================================
# DECISION CONSTANTS
# ============================================================

APPLY_NOW = "APPLY_NOW"
IMPROVE_FIRST = "IMPROVE_FIRST"
DONT_PRIORITIZE = "DONT_PRIORITIZE"


# Evidence states that represent positive support.
STRONG_STATUSES = {
    "DIRECT",
}

ACCEPTABLE_STATUSES = {
    "DIRECT",
    "RELATED",
}

WEAK_STATUSES = {
    "PARTIAL",
    "UNKNOWN",
}

MISSING_STATUS = {
    "MISSING",
}


# ============================================================
# REQUIREMENT IMPORTANCE
# ============================================================

IMPORTANCE_WEIGHT = {
    "REQUIRED": 1.00,
    "PREFERRED": 0.50,
    "NICE_TO_HAVE": 0.20,
    "UNKNOWN": 0.30,
}


# ============================================================
# EVIDENCE STATUS WEIGHTS
# ============================================================

STATUS_WEIGHT = {
    "DIRECT": 1.00,
    "RELATED": 0.70,
    "PARTIAL": 0.40,
    "UNKNOWN": 0.15,
    "MISSING": 0.00,
}


# ============================================================
# HARD REQUIREMENT TYPES
# ============================================================

HARD_REQUIREMENT_TYPES = {
    "EDUCATION",
    "EXPERIENCE",
    "CONSTRAINT",
}


# ============================================================
# ACTIONABILITY
# ============================================================

def _is_improvable_requirement(
    evidence: Dict[str, Any],
) -> bool:
    """
    Determine whether a missing/weak requirement could
    reasonably be improved.

    This is deliberately conservative.

    Examples generally considered improvable:

        SKILL
        PROJECT
        CERTIFICATION

    Examples that should not automatically be treated
    as quickly improvable:

        EXPERIENCE
        EDUCATION
        CONSTRAINT
    """

    req_type = str(
        evidence.get(
            "type",
            "SKILL",
        )
    ).upper()

    return req_type in {
        "SKILL",
        "PROJECT",
        "CERTIFICATION",
    }


# ============================================================
# REQUIREMENT HELPERS
# ============================================================

def _importance(
    evidence: Dict[str, Any],
) -> str:

    return str(
        evidence.get(
            "importance",
            "UNKNOWN",
        )
    ).upper().strip()


def _status(
    evidence: Dict[str, Any],
) -> str:

    return str(
        evidence.get(
            "status",
            "UNKNOWN",
        )
    ).upper().strip()


def _requirement_type(
    evidence: Dict[str, Any],
) -> str:

    return str(
        evidence.get(
            "type",
            "SKILL",
        )
    ).upper().strip()


def _confidence(
    evidence: Dict[str, Any],
) -> float:

    try:

        value = float(
            evidence.get(
                "confidence",
                0.0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        value = 0.0

    return max(
        0.0,
        min(
            1.0,
            value,
        ),
    )


# ============================================================
# EXPERIENCE ANALYSIS
# ============================================================

def _experience_gap(
    evidence: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze explicit experience-year evidence.

    Returns:

        required_years
        candidate_years
        gap_years
        satisfied
        status
    """

    required = evidence.get(
        "required_experience_years"
    )

    candidate = evidence.get(
        "resume_experience_years"
    )

    try:

        required = (
            float(required)
            if required is not None
            else None
        )

    except (
        TypeError,
        ValueError,
    ):

        required = None

    try:

        candidate = (
            float(candidate)
            if candidate is not None
            else None
        )

    except (
        TypeError,
        ValueError,
    ):

        candidate = None

    if required is None:

        return {
            "required_years": None,
            "candidate_years": candidate,
            "gap_years": None,
            "satisfied": None,
            "status": "UNKNOWN",
        }

    if candidate is None:

        return {
            "required_years": required,
            "candidate_years": None,
            "gap_years": None,
            "satisfied": None,
            "status": "UNKNOWN",
        }

    gap = max(
        0.0,
        required - candidate,
    )

    if candidate >= required:

        return {
            "required_years": required,
            "candidate_years": candidate,
            "gap_years": 0.0,
            "satisfied": True,
            "status": "SATISFIED",
        }

    return {
        "required_years": required,
        "candidate_years": candidate,
        "gap_years": round(
            gap,
            2,
        ),
        "satisfied": False,
        "status": "GAP",
    }


# ============================================================
# REQUIREMENT SCORE
# ============================================================

def _requirement_score(
    evidence: Dict[str, Any],
) -> float:
    """
    Calculate a supporting evidence score.

    This is NOT a hiring probability.

    It only summarizes how strongly the resume evidence
    supports this requirement.
    """

    status = _status(
        evidence
    )

    importance = _importance(
        evidence
    )

    status_score = STATUS_WEIGHT.get(
        status,
        0.15,
    )

    importance_score = IMPORTANCE_WEIGHT.get(
        importance,
        0.30,
    )

    confidence = _confidence(
        evidence
    )

    return (
        status_score
        * importance_score
        * confidence
    )


# ============================================================
# REQUIRED REQUIREMENT ANALYSIS
# ============================================================

def _analyze_required_requirement(
    evidence: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze a REQUIRED requirement.

    Returns a structured decision impact.
    """

    status = _status(
        evidence
    )

    req_type = _requirement_type(
        evidence
    )

    requirement = evidence.get(
        "requirement",
        "",
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    if req_type == "EXPERIENCE":

        experience = _experience_gap(
            evidence
        )

        if experience["satisfied"] is True:

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "SATISFIED",
                "severity": "NONE",
                "reason":
                    "Required experience is satisfied.",
            }

        if experience["status"] == "GAP":

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "BLOCKING",
                "severity": "HIGH",
                "reason":
                    "Required experience years are below "
                    "the stated minimum.",
            }

        return {
            "requirement": requirement,
            "importance": "REQUIRED",
            "type": req_type,
            "status": status,
            "impact": "UNKNOWN",
            "severity": "MEDIUM",
            "reason":
                "The resume does not provide enough "
                "documented experience information.",
        }

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    if req_type == "EDUCATION":

        if status == "DIRECT":

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "SATISFIED",
                "severity": "NONE",
                "reason":
                    "Required education has documented "
                    "support.",
            }

        if status == "RELATED":

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "REVIEW",
                "severity": "MEDIUM",
                "reason":
                    "The education appears related, but "
                    "the equivalence is not exact.",
            }

        if status == "MISSING":

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "BLOCKING",
                "severity": "HIGH",
                "reason":
                    "No documented evidence of the "
                    "required education was found.",
            }

        return {
            "requirement": requirement,
            "importance": "REQUIRED",
            "type": req_type,
            "status": status,
            "impact": "UNKNOWN",
            "severity": "MEDIUM",
            "reason":
                "Education evidence is insufficient "
                "for a confident decision.",
        }

    # --------------------------------------------------------
    # Constraints
    # --------------------------------------------------------

    if req_type == "CONSTRAINT":

        if status == "DIRECT":

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "SATISFIED",
                "severity": "NONE",
                "reason":
                    "The documented resume evidence "
                    "supports this requirement.",
            }

        if status == "MISSING":

            return {
                "requirement": requirement,
                "importance": "REQUIRED",
                "type": req_type,
                "status": status,
                "impact": "BLOCKING",
                "severity": "HIGH",
                "reason":
                    "The required constraint has no "
                    "supporting evidence.",
            }

    # --------------------------------------------------------
    # Normal skills / projects / certifications
    # --------------------------------------------------------

    if status == "DIRECT":

        return {
            "requirement": requirement,
            "importance": "REQUIRED",
            "type": req_type,
            "status": status,
            "impact": "SATISFIED",
            "severity": "NONE",
            "reason":
                "Direct documented evidence was found.",
        }

    if status == "RELATED":

        return {
            "requirement": requirement,
            "importance": "REQUIRED",
            "type": req_type,
            "status": status,
            "impact": "REVIEW",
            "severity": "MEDIUM",
            "reason":
                "Related evidence was found, but it "
                "does not exactly prove the requirement.",
        }

    if status == "PARTIAL":

        return {
            "requirement": requirement,
            "importance": "REQUIRED",
            "type": req_type,
            "status": status,
            "impact": "GAP",
            "severity": "MEDIUM",
            "reason":
                "The resume contains partial evidence "
                "but not strong direct support.",
        }

    if status == "MISSING":

        return {
            "requirement": requirement,
            "importance": "REQUIRED",
            "type": req_type,
            "status": status,
            "impact": (
                "IMPROVABLE_GAP"
                if _is_improvable_requirement(evidence)
                else "BLOCKING"
            ),
            "severity": (
                "MEDIUM"
                if _is_improvable_requirement(evidence)
                else "HIGH"
            ),
            "reason":
                "No documented evidence was found.",
        }

    return {
        "requirement": requirement,
        "importance": "REQUIRED",
        "type": req_type,
        "status": status,
        "impact": "UNKNOWN",
        "severity": "MEDIUM",
        "reason":
            "Evidence was insufficient for a confident "
            "requirement decision.",
    }


# ============================================================
# FINAL DECISION
# ============================================================

def decide_job(
    evidence_breakdown: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Convert evidence into a job-level recommendation.

    Decision logic:

        1. REQUIRED blockers are checked first.
        2. Required education / experience mismatches
           receive high severity.
        3. Missing improvable skills can produce
           IMPROVE_FIRST.
        4. Preferred and nice-to-have gaps do NOT
           automatically block application.
        5. If required requirements are sufficiently
           supported, recommendation is APPLY_NOW.

    The final result is a recommendation based on
    DOCUMENTED RESUME EVIDENCE.

    It is not a hiring prediction.
    """

    if not evidence_breakdown:

        return {
            "decision": DONT_PRIORITIZE,

            "decision_label":
                "DON'T PRIORITIZE",

            "decision_reason":
                "No job requirements were available "
                "for evaluation.",

            "supporting_score": 0.0,

            "required_total": 0,
            "required_satisfied": 0,
            "required_gaps": 0,
            "required_unknown": 0,

            "preferred_gaps": 0,
            "nice_to_have_gaps": 0,

            "blocking_requirements": [],
            "improvement_requirements": [],
            "review_requirements": [],
        }

    required = []
    preferred = []
    nice_to_have = []
    unknown_importance = []

    for evidence in evidence_breakdown:

        importance = _importance(
            evidence
        )

        if importance == "REQUIRED":

            required.append(
                evidence
            )

        elif importance == "PREFERRED":

            preferred.append(
                evidence
            )

        elif importance == "NICE_TO_HAVE":

            nice_to_have.append(
                evidence
            )

        else:

            unknown_importance.append(
                evidence
            )

    # --------------------------------------------------------
    # Analyze REQUIRED requirements
    # --------------------------------------------------------

    required_analysis = []

    for evidence in required:

        required_analysis.append(
            _analyze_required_requirement(
                evidence
            )
        )

    blocking_requirements = [
        item
        for item in required_analysis
        if item["impact"] == "BLOCKING"
    ]

    improvement_requirements = [
        item
        for item in required_analysis
        if item["impact"] == "IMPROVABLE_GAP"
    ]

    review_requirements = [
        item
        for item in required_analysis
        if item["impact"] in {
            "REVIEW",
            "UNKNOWN",
            "GAP",
        }
    ]

    required_satisfied = [
        item
        for item in required_analysis
        if item["impact"] == "SATISFIED"
    ]

    # --------------------------------------------------------
    # Supporting score
    # --------------------------------------------------------

    weighted_scores = []

    for evidence in evidence_breakdown:

        weighted_scores.append(
            _requirement_score(
                evidence
            )
        )

    if weighted_scores:

        supporting_score = (
            sum(weighted_scores)
            / max(
                1,
                len(weighted_scores),
            )
        )

    else:

        supporting_score = 0.0

    supporting_score = round(
        supporting_score * 100,
        1,
    )

    # --------------------------------------------------------
    # Count preferred/nice-to-have gaps
    # --------------------------------------------------------

    preferred_gaps = sum(
        1
        for evidence in preferred
        if _status(evidence) == "MISSING"
    )

    nice_to_have_gaps = sum(
        1
        for evidence in nice_to_have
        if _status(evidence) == "MISSING"
    )

    # --------------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------------

    # Case 1:
    # A major hard requirement is missing or failed.
    if blocking_requirements:

        decision = DONT_PRIORITIZE

        decision_reason = (
            "At least one required qualification, "
            "experience requirement, or hard requirement "
            "is not supported by the documented resume evidence."
        )

    # Case 2:
    # Required skill gap exists and is potentially
    # improvable.
    elif improvement_requirements:

        decision = IMPROVE_FIRST

        decision_reason = (
            "The candidate has some alignment, but at least "
            "one required skill has no documented evidence. "
            "Improving or demonstrating that requirement "
            "should come before prioritizing the application."
        )

    # Case 3:
    # Required evidence is uncertain or only partially
    # supported.
    elif review_requirements:

        decision = IMPROVE_FIRST

        decision_reason = (
            "The candidate has relevant evidence, but one "
            "or more required requirements are only partially "
            "supported or need review before applying."
        )

    # Case 4:
    # All required requirements satisfied.
    else:

        decision = APPLY_NOW

        decision_reason = (
            "The documented resume evidence supports the "
            "required job requirements. Preferred or "
            "nice-to-have gaps do not block the application."
        )

    # --------------------------------------------------------
    # Human-readable label
    # --------------------------------------------------------

    labels = {

        APPLY_NOW:
            "APPLY NOW",

        IMPROVE_FIRST:
            "IMPROVE FIRST",

        DONT_PRIORITIZE:
            "DON'T PRIORITIZE",
    }

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "decision": decision,

        "decision_label":
            labels[decision],

        "decision_reason":
            decision_reason,

        # Important:
        # This is a supporting evidence score, NOT a
        # probability of getting hired.
        "supporting_score":
            supporting_score,

        "required_total":
            len(required),

        "required_satisfied":
            len(required_satisfied),

        "required_gaps":
            len(
                improvement_requirements
            )
            + len(
                blocking_requirements
            ),

        "required_unknown":
            sum(
                1
                for item in required_analysis
                if item["impact"] == "UNKNOWN"
            ),

        "preferred_gaps":
            preferred_gaps,

        "nice_to_have_gaps":
            nice_to_have_gaps,

        "blocking_requirements":
            blocking_requirements,

        "improvement_requirements":
            improvement_requirements,

        "review_requirements":
            review_requirements,

        "required_analysis":
            required_analysis,
    }


# ============================================================
# CONVENIENCE API
# ============================================================

def decide_from_job_analysis(
    job_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the Decision Engine directly on the output
    of Evidence Engine's analyze_job().
    """

    evidence_breakdown = job_analysis.get(
        "evidence_breakdown",
        [],
    )

    result = decide_job(
        evidence_breakdown
    )

    # Preserve useful job context.
    result["role"] = job_analysis.get(
        "role"
    )

    result["experience"] = job_analysis.get(
        "experience"
    )

    result["resume_summary"] = job_analysis.get(
        "resume_summary"
    )

    return result


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    import json

    # --------------------------------------------------------
    # TEST 1
    #
    # Required requirements satisfied.
    # Preferred AWS missing.
    #
    # Expected:
    #
    # APPLY NOW
    # --------------------------------------------------------

    apply_case = [

        {
            "requirement": "Python",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "FastAPI",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "REST APIs",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "AWS",
            "importance": "PREFERRED",
            "type": "SKILL",
            "status": "MISSING",
            "confidence": 0.0,
        },
    ]

    print("\n" + "=" * 60)
    print("TEST 1 — PREFERRED GAP")
    print("=" * 60)

    print(
        json.dumps(
            decide_job(
                apply_case
            ),
            indent=2,
        )
    )

    # --------------------------------------------------------
    # TEST 2
    #
    # Required AWS missing.
    #
    # Expected:
    #
    # IMPROVE FIRST
    #
    # because AWS is a required SKILL and is theoretically
    # improvable.
    # --------------------------------------------------------

    improve_case = [

        {
            "requirement": "Python",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "FastAPI",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "AWS",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "MISSING",
            "confidence": 0.0,
        },
    ]

    print("\n" + "=" * 60)
    print("TEST 2 — REQUIRED SKILL GAP")
    print("=" * 60)

    print(
        json.dumps(
            decide_job(
                improve_case
            ),
            indent=2,
        )
    )

    # --------------------------------------------------------
    # TEST 3
    #
    # Required education missing.
    #
    # Expected:
    #
    # DON'T PRIORITIZE
    # --------------------------------------------------------

    hard_case = [

        {
            "requirement": "Python",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "Bachelor's degree",
            "importance": "REQUIRED",
            "type": "EDUCATION",
            "status": "MISSING",
            "confidence": 0.0,
        },
    ]

    print("\n" + "=" * 60)
    print("TEST 3 — HARD REQUIREMENT GAP")
    print("=" * 60)

    print(
        json.dumps(
            decide_job(
                hard_case
            ),
            indent=2,
        )
    )

    # --------------------------------------------------------
    # TEST 4
    #
    # Required experience satisfied.
    #
    # Expected:
    #
    # APPLY NOW
    # --------------------------------------------------------

    experience_case = [

        {
            "requirement": "Python",
            "importance": "REQUIRED",
            "type": "SKILL",
            "status": "DIRECT",
            "confidence": 0.98,
        },

        {
            "requirement": "Backend experience",
            "importance": "REQUIRED",
            "type": "EXPERIENCE",
            "status": "DIRECT",
            "confidence": 0.90,
            "required_experience_years": 2,
            "resume_experience_years": 3.5,
        },
    ]

    print("\n" + "=" * 60)
    print("TEST 4 — EXPERIENCE SATISFIED")
    print("=" * 60)

    print(
        json.dumps(
            decide_job(
                experience_case
            ),
            indent=2,
        )
    )