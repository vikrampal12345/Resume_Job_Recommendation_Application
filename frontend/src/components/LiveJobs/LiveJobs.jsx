import "./LiveJobs.css";
import { useEffect, useMemo, useState } from "react";
import API from "../../services/api";

function LiveJobs({ jobs, resumeText }) {
    const [analyzingJobId, setAnalyzingJobId] = useState(null);

    const [analysisResults, setAnalysisResults] = useState({});

    const [analysisErrors, setAnalysisErrors] = useState({});

    const [activeAnalysis, setActiveAnalysis] = useState(null);

    const [showFullDetails, setShowFullDetails] = useState(false);


    // =========================================================
    // ESCAPE TO CLOSE
    // =========================================================

    useEffect(() => {
        if (!activeAnalysis) {
            return;
        }

        const handleEscape = (event) => {
            if (event.key === "Escape") {
                setActiveAnalysis(null);
                setShowFullDetails(false);
            }
        };

        document.addEventListener(
            "keydown",
            handleEscape
        );

        return () => {
            document.removeEventListener(
                "keydown",
                handleEscape
            );
        };
    }, [activeAnalysis]);


    // =========================================================
    // BODY SCROLL LOCK
    // =========================================================

    useEffect(() => {
        if (!activeAnalysis) {
            document.body.style.overflow = "";
            return;
        }

        document.body.style.overflow = "hidden";

        return () => {
            document.body.style.overflow = "";
        };
    }, [activeAnalysis]);


    // =========================================================
    // NO JOBS
    // =========================================================

    if (!jobs || jobs.length === 0) {
        return null;
    }


    // =========================================================
    // JOB ID
    // =========================================================

    const getJobId = (job) => {
        return (
            job?.job_id ||
            `${job?.company || "company"}-${job?.job_title || "job"}-${job?.location || "location"}`
        );
    };


    // =========================================================
    // DECISION INFO
    // =========================================================

    const getDecisionInfo = (analysis) => {
        const rawDecision =
            analysis?.decision?.decision ||
            "";

        const normalized =
            String(rawDecision)
                .trim()
                .toUpperCase()
                .replace(/\s+/g, "_");

        if (
            normalized === "APPLY_NOW" ||
            normalized === "APPLY"
        ) {
            return {
                key: "APPLY_NOW",
                label: "APPLY NOW",
                tone: "success",
                icon: "✓",
            };
        }

        if (
            normalized === "IMPROVE_FIRST" ||
            normalized === "IMPROVE"
        ) {
            return {
                key: "IMPROVE_FIRST",
                label: "IMPROVE FIRST",
                tone: "warning",
                icon: "↗",
            };
        }

        return {
            key: "DONT_PRIORITIZE",
            label: "DON'T PRIORITIZE",
            tone: "danger",
            icon: "!",
        };
    };


    // =========================================================
    // DECISION REASON
    // =========================================================

    const getDecisionReason = (analysis) => {
        return (
            analysis?.decision?.decision_reason ||
            analysis?.decision?.reason ||
            "No decision explanation was returned."
        );
    };


    // =========================================================
    // SUPPORTING SCORE
    // =========================================================

    const getSupportingScore = (analysis) => {
        const rawScore = Number(
            analysis?.decision?.supporting_score
        );

        if (!Number.isFinite(rawScore)) {
            return null;
        }

        return Math.min(
            100,
            Math.max(
                0,
                Math.round(rawScore)
            )
        );
    };


    // =========================================================
    // EVIDENCE BREAKDOWN
    // Backend shape:
    //
    // evidence: {
    //     role,
    //     experience,
    //     evidence_breakdown: [...]
    // }
    // =========================================================

    const getEvidenceBreakdown = (analysis) => {
        const breakdown =
            analysis?.evidence?.evidence_breakdown;

        if (Array.isArray(breakdown)) {
            return breakdown;
        }

        if (Array.isArray(analysis?.evidence)) {
            return analysis.evidence;
        }

        return [];
    };


    // =========================================================
    // REQUIREMENTS
    // =========================================================

    const getRequirements = (analysis) => {
        if (Array.isArray(analysis?.requirements)) {
            return analysis.requirements;
        }

        return [];
    };


    // =========================================================
    // EVIDENCE STATUS
    // =========================================================

    const getEvidenceStatus = (item) => {
        return String(
            item?.status ||
            "UNKNOWN"
        )
            .trim()
            .toUpperCase()
            .replace(/\s+/g, "_");
    };


    // =========================================================
    // STATUS LABEL
    // =========================================================

    const getEvidenceLabel = (status) => {
        switch (status) {
            case "DIRECT":
            case "DIRECT_EVIDENCE":
                return "DIRECT";

            case "RELATED":
            case "RELATED_EVIDENCE":
                return "RELATED";

            case "PARTIAL":
            case "PARTIAL_EVIDENCE":
                return "PARTIAL";

            case "MISSING":
            case "MISSING_EVIDENCE":
                return "MISSING";

            default:
                return "UNKNOWN";
        }
    };


    // =========================================================
    // STATUS TONE
    // =========================================================

    const getEvidenceTone = (status) => {
        switch (status) {
            case "DIRECT":
            case "DIRECT_EVIDENCE":
                return "direct";

            case "RELATED":
            case "RELATED_EVIDENCE":
                return "related";

            case "PARTIAL":
            case "PARTIAL_EVIDENCE":
                return "partial";

            case "MISSING":
            case "MISSING_EVIDENCE":
                return "missing";

            default:
                return "unknown";
        }
    };


    // =========================================================
    // REQUIREMENT NAME
    // =========================================================

    const getRequirementName = (item) => {
        return (
            item?.requirement ||
            item?.skill ||
            item?.name ||
            item?.title ||
            "Requirement"
        );
    };


    // =========================================================
    // IMPORTANCE
    // =========================================================

    const getImportance = (item) => {
        return (
            item?.importance ||
            "UNKNOWN"
        )
            .toString()
            .toUpperCase();
    };


    // =========================================================
    // TYPE
    // =========================================================

    const getType = (item) => {
        return (
            item?.type ||
            "UNKNOWN"
        )
            .toString()
            .toUpperCase();
    };


    // =========================================================
    // LOGIC
    // =========================================================

    const getLogic = (item) => {
        return (
            item?.logic ||
            "SINGLE"
        )
            .toString()
            .toUpperCase();
    };


    // =========================================================
    // RESUME PROOF
    // =========================================================

    const getProofText = (item) => {
        return (
            item?.resume_proof ||
            item?.proof ||
            item?.proof_text ||
            ""
        );
    };


    // =========================================================
    // SOURCE SECTION
    // =========================================================

    const getSourceSection = (item) => {
        return (
            item?.source_section ||
            item?.section ||
            ""
        );
    };


    // =========================================================
    // CONFIDENCE
    // =========================================================

    const getConfidence = (item) => {
        const value = Number(
            item?.confidence
        );

        if (!Number.isFinite(value)) {
            return null;
        }

        return Math.round(
            Math.min(1, Math.max(0, value)) * 100
        );
    };


    // =========================================================
    // SIMILARITY
    // =========================================================

    const getSimilarity = (item) => {
        const value = Number(
            item?.similarity
        );

        if (!Number.isFinite(value)) {
            return null;
        }

        return Math.round(
            Math.min(1, Math.max(0, value)) * 100
        );
    };


    // =========================================================
    // OPTION RESULTS
    // =========================================================

    const getOptionResults = (item) => {
        return Array.isArray(
            item?.option_results
        )
            ? item.option_results
            : [];
    };


    // =========================================================
    // DECISION SUMMARY
    // =========================================================

    const getDecisionSummary = (analysis) => {
        const decision =
            analysis?.decision || {};

        const requiredTotal = Number(
            decision?.required_total
        );

        const requiredSatisfied = Number(
            decision?.required_satisfied
        );

        const requiredGaps = Number(
            decision?.required_gaps
        );

        const requiredUnknown = Number(
            decision?.required_unknown
        );

        const preferredGaps = Number(
            decision?.preferred_gaps
        );

        const niceToHaveGaps = Number(
            decision?.nice_to_have_gaps
        );

        return {
            requiredTotal:
                Number.isFinite(requiredTotal)
                    ? requiredTotal
                    : null,

            requiredSatisfied:
                Number.isFinite(requiredSatisfied)
                    ? requiredSatisfied
                    : null,

            requiredGaps:
                Number.isFinite(requiredGaps)
                    ? requiredGaps
                    : null,

            requiredUnknown:
                Number.isFinite(requiredUnknown)
                    ? requiredUnknown
                    : null,

            preferredGaps:
                Number.isFinite(preferredGaps)
                    ? preferredGaps
                    : null,

            niceToHaveGaps:
                Number.isFinite(niceToHaveGaps)
                    ? niceToHaveGaps
                    : null,
        };
    };


    // =========================================================
    // REQUIREMENT GROUPS FROM DECISION ENGINE
    // =========================================================

    const getBlockingRequirements = (analysis) => {
        return Array.isArray(
            analysis?.decision?.blocking_requirements
        )
            ? analysis.decision.blocking_requirements
            : [];
    };


    const getImprovementRequirements = (analysis) => {
        return Array.isArray(
            analysis?.decision?.improvement_requirements
        )
            ? analysis.decision.improvement_requirements
            : [];
    };


    const getReviewRequirements = (analysis) => {
        return Array.isArray(
            analysis?.decision?.review_requirements
        )
            ? analysis.decision.review_requirements
            : [];
    };


    const getRequiredAnalysis = (analysis) => {
        return Array.isArray(
            analysis?.decision?.required_analysis
        )
            ? analysis.decision.required_analysis
            : [];
    };


    // =========================================================
    // ANALYZE JOB
    // =========================================================

    const analyzeJob = async (job) => {
        const jobId = getJobId(job);

        if (!resumeText || !resumeText.trim()) {
            setAnalysisErrors((previous) => ({
                ...previous,
                [jobId]:
                    "Resume text is not available. Please analyze your resume again.",
            }));

            return;
        }

        try {
            setAnalyzingJobId(jobId);

            setAnalysisErrors((previous) => ({
                ...previous,
                [jobId]: "",
            }));

            const response = await API.post(
                "/analyze-job",
                {
                    company:
                        job?.company || "",

                    job_title:
                        job?.job_title || "",

                    location:
                        job?.location || "",

                    employment_type:
                        job?.employment_type || "",

                    salary:
                        job?.salary || null,

                    posted_date:
                        job?.posted_date || null,

                    apply_link:
                        job?.apply_link || "",

                    job_id:
                        job?.job_id || null,

                    resume_text:
                        resumeText,

                    job_description:
                        job?.job_description || "",
                }
            );

            const result = response?.data;

            setAnalysisResults((previous) => ({
                ...previous,
                [jobId]: result,
            }));

            setShowFullDetails(false);

            setActiveAnalysis({
                jobId,
                job,
                analysis: result,
            });

        } catch (error) {
            console.error(
                "Job analysis error:",
                error
            );

            const message =
                error?.response?.data?.detail ||
                "Unable to analyze this job right now.";

            setAnalysisErrors((previous) => ({
                ...previous,
                [jobId]: message,
            }));
        } finally {
            setAnalyzingJobId(null);
        }
    };


    // =========================================================
    // OPEN EXISTING ANALYSIS
    // =========================================================

    const openExistingAnalysis = (job) => {
        const jobId = getJobId(job);

        const result =
            analysisResults[jobId];

        if (!result) {
            analyzeJob(job);
            return;
        }

        setShowFullDetails(false);

        setActiveAnalysis({
            jobId,
            job,
            analysis: result,
        });
    };


    // =========================================================
    // ANALYZE CLICK
    // =========================================================

    const handleAnalyzeClick = (job) => {
        const jobId = getJobId(job);

        if (analysisResults[jobId]) {
            openExistingAnalysis(job);
            return;
        }

        analyzeJob(job);
    };


    // =========================================================
    // CLOSE MODAL
    // =========================================================

    const closeAnalysisModal = () => {
        setActiveAnalysis(null);
        setShowFullDetails(false);
    };


    // =========================================================
    // APPLY
    // =========================================================

    const handleApply = (job) => {
        const link = job?.apply_link;

        if (!link) {
            return;
        }

        window.open(
            link,
            "_blank",
            "noopener,noreferrer"
        );
    };


    // =========================================================
    // ACTIVE ANALYSIS DATA
    // =========================================================

    const activeAnalysisData =
        activeAnalysis?.analysis;

    const activeDecision =
        activeAnalysisData
            ? getDecisionInfo(
                activeAnalysisData
            )
            : null;

    const activeScore =
        activeAnalysisData
            ? getSupportingScore(
                activeAnalysisData
            )
            : null;

    const evidenceBreakdown =
        activeAnalysisData
            ? getEvidenceBreakdown(
                activeAnalysisData
            )
            : [];

    const requirements =
        activeAnalysisData
            ? getRequirements(
                activeAnalysisData
            )
            : [];

    const decisionSummary =
        activeAnalysisData
            ? getDecisionSummary(
                activeAnalysisData
            )
            : null;

    const blockingRequirements =
        activeAnalysisData
            ? getBlockingRequirements(
                activeAnalysisData
            )
            : [];

    const improvementRequirements =
        activeAnalysisData
            ? getImprovementRequirements(
                activeAnalysisData
            )
            : [];

    const reviewRequirements =
        activeAnalysisData
            ? getReviewRequirements(
                activeAnalysisData
            )
            : [];

    const requiredAnalysis =
        activeAnalysisData
            ? getRequiredAnalysis(
                activeAnalysisData
            )
            : [];


    // =========================================================
    // REQUIREMENT MAP
    // =========================================================

    const requirementMap = useMemo(() => {
        const map = new Map();

        requirements.forEach((item) => {
            map.set(
                getRequirementName(item).toLowerCase(),
                item
            );
        });

        return map;
    }, [requirements]);


    // =========================================================
    // RENDER
    // =========================================================

    return (
        <section className="live-jobs-section">

            {/* =====================================================
                HEADER
            ===================================================== */}

            <div className="live-jobs-header">

                <div>
                    <span className="live-jobs-kicker">
                        LIVE OPPORTUNITIES
                    </span>

                    <h2>
                        Jobs matched to your target role
                    </h2>

                    <p>
                        Review a live opening and use Syncronal
                        to understand whether your resume supports
                        its requirements.
                    </p>
                </div>

                <span className="live-jobs-count">
                    {jobs.length} jobs
                </span>

            </div>


            {/* =====================================================
                JOB GRID
            ===================================================== */}

            <div className="live-jobs-grid">

                {jobs.map((job, index) => {

                    const jobId =
                        getJobId(job);

                    const isAnalyzing =
                        analyzingJobId === jobId;

                    const hasAnalysis =
                        Boolean(
                            analysisResults[jobId]
                        );

                    const hasError =
                        Boolean(
                            analysisErrors[jobId]
                        );

                    return (
                        <article
                            className="job-card"
                            key={jobId || index}
                        >

                            {/* CARD TOP */}

                            <div className="job-card-top">

                                <div className="job-company-mark">
                                    {(
                                        job?.company ||
                                        "C"
                                    )
                                        .charAt(0)
                                        .toUpperCase()}
                                </div>

                                <span className="job-ai-badge">
                                    AI READY
                                </span>

                            </div>


                            {/* TITLE */}

                            <div className="job-card-heading">

                                <h3>
                                    {job?.job_title ||
                                        "Untitled Position"}
                                </h3>

                                <p>
                                    {job?.company ||
                                        "Company not available"}
                                </p>

                            </div>


                            {/* META */}

                            <div className="job-metadata">

                                <div className="job-meta-item">

                                    <span>
                                        LOCATION
                                    </span>

                                    <strong>
                                        {job?.location ||
                                            "Not Mentioned"}
                                    </strong>

                                </div>


                                <div className="job-meta-item">

                                    <span>
                                        EMPLOYMENT
                                    </span>

                                    <strong>
                                        {job?.employment_type ||
                                            "Not Mentioned"}
                                    </strong>

                                </div>


                                <div className="job-meta-item">

                                    <span>
                                        SALARY
                                    </span>

                                    <strong>
                                        {job?.salary ||
                                            "Not Mentioned"}
                                    </strong>

                                </div>


                                <div className="job-meta-item">

                                    <span>
                                        POSTED
                                    </span>

                                    <strong>
                                        {job?.posted_date ||
                                            "Not Mentioned"}
                                    </strong>

                                </div>

                            </div>


                            {/* ERROR */}

                            {hasError && (
                                <div className="job-analysis-error">
                                    {analysisErrors[jobId]}
                                </div>
                            )}


                            {/* ACTIONS */}

                            <div className="job-card-actions">

                                <button
                                    type="button"
                                    className={`job-analyze-button ${
                                        hasAnalysis
                                            ? "has-analysis"
                                            : ""
                                    }`}
                                    onClick={() =>
                                        handleAnalyzeClick(job)
                                    }
                                    disabled={isAnalyzing}
                                >

                                    <span className="job-analyze-icon">
                                        ✦
                                    </span>

                                    <span>
                                        {isAnalyzing
                                            ? "Analyzing..."
                                            : hasAnalysis
                                            ? "View AI Analysis"
                                            : "Analyze by AI"}
                                    </span>

                                </button>


                                <button
                                    type="button"
                                    className="job-apply-button"
                                    onClick={() =>
                                        handleApply(job)
                                    }
                                    disabled={
                                        !job?.apply_link
                                    }
                                >
                                    Apply
                                </button>

                            </div>

                        </article>
                    );
                })}

            </div>


            {/* =====================================================
                ANALYSIS MODAL
            ===================================================== */}

            {activeAnalysis && (
                <div
                    className="analysis-modal-overlay"
                    onClick={closeAnalysisModal}
                >

                    <div
                        className="analysis-modal"
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                    >

                        {/* =================================================
                            HEADER
                        ================================================= */}

                        <div className="analysis-modal-header">

                            <div className="analysis-modal-title-group">

                                <span className="analysis-modal-kicker">
                                    AI JOB ANALYSIS
                                </span>

                                <h2>
                                    Should you apply?
                                </h2>

                                <div className="analysis-job-title">
                                    {
                                        activeAnalysis.job?.job_title ||
                                        "Untitled Position"
                                    }
                                </div>

                                <div className="analysis-job-company">

                                    {
                                        activeAnalysis.job?.company ||
                                        "Company not available"
                                    }

                                    <span>
                                        •
                                    </span>

                                    {
                                        activeAnalysis.job?.location ||
                                        "Location not available"
                                    }

                                </div>

                            </div>


                            <button
                                type="button"
                                className="analysis-modal-close"
                                onClick={closeAnalysisModal}
                                aria-label="Close analysis"
                            >
                                ×
                            </button>

                        </div>


                        {/* =================================================
                            DECISION
                        ================================================= */}

                        <div
                            className={`analysis-decision-card ${
                                activeDecision?.tone ||
                                "danger"
                            }`}
                        >

                            <div className="decision-main">

                                <div className="decision-icon">
                                    {
                                        activeDecision?.icon ||
                                        "!"
                                    }
                                </div>

                                <div>

                                    <span className="decision-eyebrow">
                                        RECOMMENDATION
                                    </span>

                                    <h3>
                                        {
                                            activeDecision?.label ||
                                            "DON'T PRIORITIZE"
                                        }
                                    </h3>

                                </div>

                            </div>


                            <div className="decision-score-block">

                                <span>
                                    SUPPORTING EVIDENCE
                                </span>

                                <strong>
                                    {activeScore !== null
                                        ? `${activeScore}%`
                                        : "—"}
                                </strong>

                            </div>

                        </div>


                        {/* =================================================
                            REASON
                        ================================================= */}

                        <div className="analysis-reason">

                            <span className="section-eyebrow">
                                WHY THIS DECISION
                            </span>

                            <p>
                                {getDecisionReason(
                                    activeAnalysisData
                                )}
                            </p>

                        </div>


                        {/* =================================================
                            SUMMARY
                        ================================================= */}

                        {decisionSummary && (
                            <div className="analysis-summary-row">

                                <div className="summary-card">

                                    <span>
                                        Required support
                                    </span>

                                    <strong>
                                        {
                                            decisionSummary.requiredSatisfied ??
                                            0
                                        }
                                        /
                                        {
                                            decisionSummary.requiredTotal ??
                                            0
                                        }
                                    </strong>

                                    <small>
                                        requirements supported
                                    </small>

                                </div>


                                <div className="summary-card">

                                    <span>
                                        Required gaps
                                    </span>

                                    <strong>
                                        {
                                            decisionSummary.requiredGaps ??
                                            0
                                        }
                                    </strong>

                                    <small>
                                        missing or unsupported
                                    </small>

                                </div>


                                <div className="summary-card">

                                    <span>
                                        Preferred gaps
                                    </span>

                                    <strong>
                                        {
                                            decisionSummary.preferredGaps ??
                                            0
                                        }
                                    </strong>

                                    <small>
                                        areas to strengthen
                                    </small>

                                </div>

                            </div>
                        )}


                        {/* =================================================
                            VIEW DETAILS CTA
                        ================================================= */}

                        <div className="analysis-details-toggle">

                            <div>

                                <span className="section-eyebrow">
                                    EVIDENCE REVIEW
                                </span>

                                <h3>
                                    {showFullDetails
                                        ? "Full analysis"
                                        : "Want to know exactly why?"}
                                </h3>

                                <p>
                                    {showFullDetails
                                        ? "Showing the complete requirement, evidence and decision breakdown."
                                        : "See what the job requires, what your resume proves, and which gaps affect the decision."}
                                </p>

                            </div>


                            <button
                                type="button"
                                className="view-details-button"
                                onClick={() =>
                                    setShowFullDetails(
                                        (previous) => !previous
                                    )
                                }
                            >
                                {showFullDetails
                                    ? "Hide Details"
                                    : "View Full Details"}

                                <span>
                                    {showFullDetails
                                        ? "↑"
                                        : "↓"}
                                </span>
                            </button>

                        </div>


                        {/* =================================================
                            FULL DETAILS
                        ================================================= */}

                        {showFullDetails && (
                            <div className="full-analysis-details">

                                {/* =========================================
                                    BLOCKING GAPS
                                ========================================= */}

                                {blockingRequirements.length > 0 && (
                                    <div className="detail-section">

                                        <div className="detail-section-header">

                                            <div>
                                                <span className="section-eyebrow danger-eyebrow">
                                                    BLOCKING
                                                </span>

                                                <h3>
                                                    Requirements that block the application
                                                </h3>
                                            </div>

                                            <span className="detail-count danger-count">
                                                {blockingRequirements.length}
                                            </span>

                                        </div>


                                        <div className="decision-gap-list">

                                            {blockingRequirements.map(
                                                (item, index) => (
                                                    <div
                                                        className="decision-gap-item blocking"
                                                        key={`blocking-${index}`}
                                                    >

                                                        <div className="gap-title-row">

                                                            <h4>
                                                                {
                                                                    item?.requirement ||
                                                                    "Requirement"
                                                                }
                                                            </h4>

                                                            <span>
                                                                {
                                                                    item?.severity ||
                                                                    "HIGH"
                                                                }
                                                            </span>

                                                        </div>

                                                        <p>
                                                            {
                                                                item?.reason ||
                                                                "No supporting evidence was found."
                                                            }
                                                        </p>

                                                    </div>
                                                )
                                            )}

                                        </div>

                                    </div>
                                )}


                                {/* =========================================
                                    IMPROVEMENT GAPS
                                ========================================= */}

                                {improvementRequirements.length > 0 && (
                                    <div className="detail-section">

                                        <div className="detail-section-header">

                                            <div>
                                                <span className="section-eyebrow warning-eyebrow">
                                                    IMPROVEMENT
                                                </span>

                                                <h3>
                                                    Requirements that can be strengthened
                                                </h3>
                                            </div>

                                            <span className="detail-count warning-count">
                                                {improvementRequirements.length}
                                            </span>

                                        </div>


                                        <div className="decision-gap-list">

                                            {improvementRequirements.map(
                                                (item, index) => (
                                                    <div
                                                        className="decision-gap-item improvement"
                                                        key={`improve-${index}`}
                                                    >

                                                        <div className="gap-title-row">

                                                            <h4>
                                                                {
                                                                    item?.requirement ||
                                                                    "Requirement"
                                                                }
                                                            </h4>

                                                            <span>
                                                                {
                                                                    item?.severity ||
                                                                    "MEDIUM"
                                                                }
                                                            </span>

                                                        </div>

                                                        <p>
                                                            {
                                                                item?.reason ||
                                                                "The requirement needs stronger evidence."
                                                            }
                                                        </p>

                                                    </div>
                                                )
                                            )}

                                        </div>

                                    </div>
                                )}


                                {/* =========================================
                                    REVIEW
                                ========================================= */}

                                {reviewRequirements.length > 0 && (
                                    <div className="detail-section">

                                        <div className="detail-section-header">

                                            <div>
                                                <span className="section-eyebrow">
                                                    REVIEW
                                                </span>

                                                <h3>
                                                    Requirements needing human review
                                                </h3>
                                            </div>

                                            <span className="detail-count">
                                                {reviewRequirements.length}
                                            </span>

                                        </div>


                                        <div className="decision-gap-list">

                                            {reviewRequirements.map(
                                                (item, index) => (
                                                    <div
                                                        className="decision-gap-item review"
                                                        key={`review-${index}`}
                                                    >

                                                        <div className="gap-title-row">

                                                            <h4>
                                                                {
                                                                    item?.requirement ||
                                                                    "Requirement"
                                                                }
                                                            </h4>

                                                            <span>
                                                                {
                                                                    item?.status ||
                                                                    "REVIEW"
                                                                }
                                                            </span>

                                                        </div>

                                                        <p>
                                                            {
                                                                item?.reason ||
                                                                "The evidence is not strong enough to automatically classify."
                                                            }
                                                        </p>

                                                    </div>
                                                )
                                            )}

                                        </div>

                                    </div>
                                )}


                                {/* =========================================
                                    REQUIREMENT-BY-REQUIREMENT
                                ========================================= */}

                                <div className="detail-section">

                                    <div className="detail-section-header">

                                        <div>
                                            <span className="section-eyebrow">
                                                RESUME EVIDENCE
                                            </span>

                                            <h3>
                                                Every requirement, matched to evidence
                                            </h3>
                                        </div>

                                        <span className="detail-count">
                                            {evidenceBreakdown.length}
                                        </span>

                                    </div>


                                    {evidenceBreakdown.length > 0 ? (

                                        <div className="analysis-evidence-list">

                                            {evidenceBreakdown.map(
                                                (item, index) => {

                                                    const status =
                                                        getEvidenceStatus(
                                                            item
                                                        );

                                                    const tone =
                                                        getEvidenceTone(
                                                            status
                                                        );

                                                    const requirementName =
                                                        getRequirementName(
                                                            item
                                                        );

                                                    const proof =
                                                        getProofText(
                                                            item
                                                        );

                                                    const sourceSection =
                                                        getSourceSection(
                                                            item
                                                        );

                                                    const confidence =
                                                        getConfidence(
                                                            item
                                                        );

                                                    const similarity =
                                                        getSimilarity(
                                                            item
                                                        );

                                                    const optionResults =
                                                        getOptionResults(
                                                            item
                                                        );

                                                    const relatedRequirement =
                                                        requirementMap.get(
                                                            requirementName.toLowerCase()
                                                        );

                                                    const importance =
                                                        getImportance(
                                                            item
                                                        ) !== "UNKNOWN"
                                                            ? getImportance(item)
                                                            : getImportance(
                                                                relatedRequirement || {}
                                                            );

                                                    const type =
                                                        getType(
                                                            item
                                                        ) !== "UNKNOWN"
                                                            ? getType(item)
                                                            : getType(
                                                                relatedRequirement || {}
                                                            );

                                                    return (
                                                        <div
                                                            className={`evidence-item ${tone}`}
                                                            key={
                                                                `${requirementName}-${index}`
                                                            }
                                                        >

                                                            {/* TOP */}

                                                            <div className="evidence-item-top">

                                                                <div className="evidence-requirement-heading">

                                                                    <div className="evidence-title-line">

                                                                        <h4>
                                                                            {requirementName}
                                                                        </h4>

                                                                        <span
                                                                            className={`evidence-status ${tone}`}
                                                                        >
                                                                            {
                                                                                getEvidenceLabel(
                                                                                    status
                                                                                )
                                                                            }
                                                                        </span>

                                                                    </div>


                                                                    <div className="evidence-tags">

                                                                        <span>
                                                                            {importance}
                                                                        </span>

                                                                        <span>
                                                                            {type}
                                                                        </span>

                                                                        {item?.logic &&
                                                                            item.logic !== "SINGLE" && (
                                                                                <span>
                                                                                    {item.logic}
                                                                                </span>
                                                                            )}

                                                                    </div>

                                                                </div>

                                                            </div>


                                                            {/* PROOF */}

                                                            {proof && (
                                                                <div className="evidence-proof">

                                                                    <span>
                                                                        RESUME PROOF
                                                                    </span>

                                                                    <p>
                                                                        {proof}
                                                                    </p>

                                                                </div>
                                                            )}


                                                            {/* SOURCE */}

                                                            {sourceSection && (
                                                                <div className="evidence-source">
                                                                    Source section:{" "}
                                                                    <strong>
                                                                        {sourceSection}
                                                                    </strong>
                                                                </div>
                                                            )}


                                                            {/* METRICS */}

                                                            {(confidence !== null ||
                                                                similarity !== null) && (
                                                                <div className="evidence-metrics">

                                                                    {confidence !== null && (
                                                                        <span>
                                                                            Confidence{" "}
                                                                            <strong>
                                                                                {confidence}%
                                                                            </strong>
                                                                        </span>
                                                                    )}

                                                                    {similarity !== null && (
                                                                        <span>
                                                                            Similarity{" "}
                                                                            <strong>
                                                                                {similarity}%
                                                                            </strong>
                                                                        </span>
                                                                    )}

                                                                </div>
                                                            )}


                                                            {/* GROUP OPTIONS */}

                                                            {optionResults.length > 0 && (
                                                                <div className="option-results">

                                                                    <span>
                                                                        OPTION BREAKDOWN
                                                                    </span>

                                                                    {optionResults.map(
                                                                        (option, optionIndex) => {

                                                                            const optionStatus =
                                                                                getEvidenceStatus(
                                                                                    option
                                                                                );

                                                                            return (
                                                                                <div
                                                                                    className="option-result"
                                                                                    key={optionIndex}
                                                                                >

                                                                                    <strong>
                                                                                        {
                                                                                            option?.option ||
                                                                                            "Option"
                                                                                        }
                                                                                    </strong>

                                                                                    <span
                                                                                        className={`option-result-status ${getEvidenceTone(
                                                                                            optionStatus
                                                                                        )}`}
                                                                                    >
                                                                                        {
                                                                                            getEvidenceLabel(
                                                                                                optionStatus
                                                                                            )
                                                                                        }
                                                                                    </span>

                                                                                </div>
                                                                            );
                                                                        }
                                                                    )}

                                                                </div>
                                                            )}

                                                        </div>
                                                    );
                                                }
                                            )}

                                        </div>

                                    ) : (
                                        <div className="empty-evidence">
                                            No evidence breakdown was returned.
                                        </div>
                                    )}

                                </div>


                                {/* =========================================
                                    REQUIRED ANALYSIS
                                ========================================= */}

                                {requiredAnalysis.length > 0 && (
                                    <div className="detail-section">

                                        <div className="detail-section-header">

                                            <div>
                                                <span className="section-eyebrow">
                                                    DECISION AUDIT
                                                </span>

                                                <h3>
                                                    Required requirement analysis
                                                </h3>
                                            </div>

                                            <span className="detail-count">
                                                {requiredAnalysis.length}
                                            </span>

                                        </div>


                                        <div className="required-analysis-list">

                                            {requiredAnalysis.map(
                                                (item, index) => (
                                                    <div
                                                        className="required-analysis-item"
                                                        key={`required-${index}`}
                                                    >

                                                        <div>
                                                            <strong>
                                                                {
                                                                    item?.requirement ||
                                                                    "Requirement"
                                                                }
                                                            </strong>

                                                            <span>
                                                                {
                                                                    item?.importance ||
                                                                    "REQUIRED"
                                                                }
                                                            </span>
                                                        </div>


                                                        <div
                                                            className={`required-analysis-status ${
                                                                getEvidenceTone(
                                                                    getEvidenceStatus(
                                                                        item
                                                                    )
                                                                )
                                                            }`}
                                                        >
                                                            {
                                                                getEvidenceLabel(
                                                                    getEvidenceStatus(
                                                                        item
                                                                    )
                                                                )
                                                            }
                                                        </div>


                                                        <p>
                                                            {
                                                                item?.reason ||
                                                                "No decision reason provided."
                                                            }
                                                        </p>

                                                    </div>
                                                )
                                            )}

                                        </div>

                                    </div>
                                )}

                            </div>
                        )}


                        {/* =================================================
                            FOOTER
                        ================================================= */}

                        <div className="analysis-modal-footer">

                            <button
                                type="button"
                                className="analysis-close-button"
                                onClick={closeAnalysisModal}
                            >
                                Close
                            </button>


                            <button
                                type="button"
                                className="analysis-apply-button"
                                onClick={() =>
                                    handleApply(
                                        activeAnalysis.job
                                    )
                                }
                                disabled={
                                    !activeAnalysis.job?.apply_link
                                }
                            >
                                Apply Now
                            </button>

                        </div>

                    </div>

                </div>
            )}

        </section>
    );
}

export default LiveJobs;