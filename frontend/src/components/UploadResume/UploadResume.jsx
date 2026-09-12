import "./UploadResume.css";
import { useEffect, useRef, useState } from "react";
import { uploadResume, fetchLiveJobs } from "../../services/resumeService";
import LiveJobs from "../LiveJobs/LiveJobs";

function UploadResume() {
    const [selectedFile, setSelectedFile] = useState(null);

    const [loading, setLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState("Analyzing Resume");
    const [loadingDots, setLoadingDots] = useState("");

    const [recommendations, setRecommendations] = useState([]);
    const [resumeText, setResumeText] = useState("");
    const [liveJobs, setLiveJobs] = useState([]);

    const [loadingJobs, setLoadingJobs] = useState(false);

    const [showRoleModal, setShowRoleModal] = useState(false);
    const [selectedRole, setSelectedRole] = useState("");
    const [manualRole, setManualRole] = useState("");

    const [error, setError] = useState("");

    const fileInputRef = useRef(null);


    // =========================================================
    // LOADING DOTS
    // =========================================================

    useEffect(() => {
        if (!loading && !loadingJobs) {
            setLoadingDots("");
            return;
        }

        const interval = setInterval(() => {
            setLoadingDots((previous) => {
                return previous === "..." ? "" : `${previous}.`;
            });
        }, 400);

        return () => clearInterval(interval);
    }, [loading, loadingJobs]);


    // =========================================================
    // FILE CHANGE
    // =========================================================

    const handleFileChange = (event) => {
        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        setSelectedFile(file);

        setRecommendations([]);
        setResumeText("");
        setLiveJobs([]);

        setSelectedRole("");
        setManualRole("");

        setError("");
    };


    // =========================================================
    // BROWSE
    // =========================================================

    const handleBrowseClick = () => {
        fileInputRef.current?.click();
    };


    // =========================================================
    // DRAG & DROP
    // =========================================================

    const handleDrop = (event) => {
        event.preventDefault();

        const file = event.dataTransfer.files?.[0];

        if (!file) {
            return;
        }

        setSelectedFile(file);

        setRecommendations([]);
        setResumeText("");
        setLiveJobs([]);

        setSelectedRole("");
        setManualRole("");

        setError("");
    };


    const handleDragOver = (event) => {
        event.preventDefault();
    };


    // =========================================================
    // ANALYZE RESUME
    // =========================================================
    const analyzeResume = async () => {
        if (!selectedFile) {
            setError("Please upload a resume first.");
            return;
        }

        try {
            // Clear previous state before starting a new analysis
            setError("");
            setRecommendations([]);
            setResumeText("");
            setLiveJobs([]);
            setSelectedRole("");
            setManualRole("");

            setLoading(true);
            setLoadingMessage("Analyzing Resume");

            const result = await uploadResume(selectedFile);

            const resumeRecommendations =
                Array.isArray(result?.recommendations)
                    ? result.recommendations
                    : [];

            const extractedResumeText =
                typeof result?.resume_text === "string"
                    ? result.resume_text
                    : "";

            setRecommendations(resumeRecommendations);
            setResumeText(extractedResumeText);
            setLiveJobs([]);

            setSelectedRole("");
            setManualRole("");

            if (resumeRecommendations.length === 0) {
                setError(
                    "Resume analyzed successfully, but no job recommendations were found."
                );
            }

        } catch (err) {
            console.error("Resume analysis error:", err);

            // Make sure invalid upload cannot leave stale results on screen
            setRecommendations([]);
            setResumeText("");
            setLiveJobs([]);
            setSelectedRole("");
            setManualRole("");

            // uploadResume() now throws a normal Error with the backend message
            setError(
                err?.message ||
                "Unable to analyze the resume. Please try again."
            );

        } finally {
            setLoading(false);
        }
    };
    


    // =========================================================
    // GET ROLE LABEL
    // =========================================================

    const getRecommendationLabel = (item) => {
        if (typeof item === "string") {
            return item.trim();
        }

        if (!item || typeof item !== "object") {
            return "";
        }

        return (
            item.job_role ||
            item.role ||
            item.title ||
            item.job_title ||
            item.recommendation ||
            item.name ||
            ""
        ).trim();
    };


    // =========================================================
    // GET SCORE
    //
    // 0.84 -> 84%
    // 8.4  -> 84%
    // 84   -> 84%
    // =========================================================

    const getRecommendationScore = (item) => {
        const rawScore = Number(item?.score);

        if (!Number.isFinite(rawScore)) {
            return null;
        }

        let percentage;

        if (rawScore <= 1) {
            percentage = rawScore * 100;
        } else if (rawScore <= 10) {
            percentage = rawScore * 10;
        } else {
            percentage = rawScore;
        }

        return Math.min(
            100,
            Math.max(0, Math.round(percentage))
        );
    };


    // =========================================================
    // ROLE SELECTOR
    // =========================================================

    const openRoleSelector = () => {
        setError("");
        setShowRoleModal(true);
    };


    const closeRoleSelector = () => {
        if (loadingJobs) {
            return;
        }

        setShowRoleModal(false);
    };


    // =========================================================
    // RECOMMENDED ROLE
    // =========================================================

    const handleRecommendedRoleSelect = (role) => {
        const cleanedRole = role.trim();

        if (!cleanedRole) {
            return;
        }

        setSelectedRole(cleanedRole);
        setManualRole("");
        setError("");
    };


    // =========================================================
    // MANUAL ROLE
    // =========================================================

    const handleManualRoleChange = (event) => {
        const value = event.target.value;

        setManualRole(value);
        setSelectedRole("");
        setError("");
    };


    // =========================================================
    // FIND LIVE JOBS
    // =========================================================

    const handleRoleContinue = async () => {
        const typedRole = manualRole.trim();
        const recommendedRole = selectedRole.trim();

        const targetRole = typedRole || recommendedRole;

        if (!targetRole) {
            setError(
                "Please select a recommended role or enter a role manually."
            );

            return;
        }

        // Close immediately.
        setShowRoleModal(false);

        try {
            setError("");
            setLoadingJobs(true);
            setLoadingMessage("Finding Live Jobs");

            console.log(
                "Searching jobs for target role:",
                targetRole
            );

            const result = await fetchLiveJobs(targetRole);

            const jobs = Array.isArray(result?.jobs)
                ? result.jobs
                : [];

            setLiveJobs(jobs);

            if (jobs.length === 0) {
                setError(
                    `No live jobs were found for "${targetRole}".`
                );
            }
        } catch (err) {
            console.error("Live jobs fetch error:", err);

            setLiveJobs([]);

            setError(
                err?.response?.data?.detail ||
                `Unable to fetch live jobs for "${targetRole}".`
            );
        } finally {
            setLoadingJobs(false);
        }
    };


    // =========================================================
    // STATE
    // =========================================================

    const hasRecommendations = recommendations.length > 0;


    // =========================================================
    // RENDER
    // =========================================================

    return (
        <section
            className={`upload-section ${
                hasRecommendations
                    ? "results-state"
                    : "initial-state"
            }`}
        >

            <div className="upload-container">

                {/* =================================================
                    UPLOAD + RECOMMENDATIONS
                ================================================= */}

                <div
                    className={`analysis-layout ${
                        hasRecommendations
                            ? "has-results"
                            : "no-results"
                    }`}
                >

                    {/* =================================================
                        UPLOAD CARD
                    ================================================= */}

                    <div className="upload-panel">

                        <div
                            className="upload-box"
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                        >

                            {/* ICON */}
                            <div className="upload-icon">

                                <svg
                                    viewBox="0 0 48 48"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    aria-hidden="true"
                                >
                                    <path
                                        d="M16 7H28L36 15V38C36 39.6569 34.6569 41 33 41H16C14.3431 41 13 39.6569 13 38V10C13 8.34315 14.3431 7 16 7Z"
                                        stroke="currentColor"
                                        strokeWidth="2.2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                    />

                                    <path
                                        d="M28 7V15H36"
                                        stroke="currentColor"
                                        strokeWidth="2.2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                    />

                                    <path
                                        d="M19 22H30"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                    />

                                    <path
                                        d="M19 28H30"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                    />

                                    <path
                                        d="M19 34H26"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                    />
                                </svg>

                            </div>


                            {/* TITLE */}
                            <h2>
                                Upload Resume
                            </h2>


                            <p className="upload-description">
                                Drag &amp; Drop your resume here
                            </p>


                            <p className="upload-browse-description">
                                or click below to browse
                            </p>


                            {/* BROWSE */}
                            <button
                                type="button"
                                className="browse-button"
                                onClick={handleBrowseClick}
                                disabled={loading}
                            >
                                Browse Files
                            </button>


                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf,.doc,.docx"
                                onChange={handleFileChange}
                                hidden
                            />


                            {/* FORMATS */}
                            <p className="upload-format">
                                Supported Formats: PDF • DOCX
                            </p>


                            {/* FILE */}
                            <div
                                className={`selected-file ${
                                    selectedFile
                                        ? "has-file"
                                        : "empty-file"
                                }`}
                            >
                                <span className="selected-file-name">
                                    {selectedFile
                                        ? selectedFile.name
                                        : "No file selected"}
                                </span>
                            </div>


                            {/* ANALYZE */}
                            <button
                                type="button"
                                className="analyze-button"
                                onClick={analyzeResume}
                                disabled={
                                    !selectedFile ||
                                    loading
                                }
                            >
                                {loading
                                    ? `${loadingMessage}${loadingDots}`
                                    : "Analyze Resume"}
                            </button>


                            {error && !showRoleModal && (
                                <div className="upload-error">
                                    {error}
                                </div>
                            )}

                        </div>
                    </div>


                    {/* =================================================
                        AI RECOMMENDATIONS
                    ================================================= */}

                    {hasRecommendations && (
                        <div className="recommendation-panel">

                            <div className="recommendation-header">

                                <div className="recommendation-heading-row">

                                    <div>
                                        <span className="recommendation-kicker">
                                            AI Analysis
                                        </span>

                                        <h2>
                                            Top Job Recommendations
                                        </h2>
                                    </div>

                                    <span className="recommendation-count">
                                        Top 5
                                    </span>

                                </div>


                                <p>
                                    Roles matched from your resume
                                    skills and experience.
                                </p>

                            </div>


                            <div className="recommendation-list">

                                {recommendations
                                    .slice(0, 5)
                                    .map((item, index) => {

                                        const role =
                                            getRecommendationLabel(item);

                                        const score =
                                            getRecommendationScore(item);

                                        if (!role) {
                                            return null;
                                        }

                                        const isSelected =
                                            selectedRole === role;

                                        return (
                                            <button
                                                type="button"
                                                className={`recommendation-card ${
                                                    isSelected
                                                        ? "active"
                                                        : ""
                                                }`}
                                                key={`${role}-${index}`}
                                                onClick={() =>
                                                    handleRecommendedRoleSelect(
                                                        role
                                                    )
                                                }
                                            >

                                                <div className="recommendation-rank">
                                                    {index + 1}
                                                </div>


                                                <div className="recommendation-content">

                                                    <div className="recommendation-title-row">

                                                        <h3>
                                                            {role}
                                                        </h3>

                                                        {score !== null && (
                                                            <span className="recommendation-score">
                                                                {score}%
                                                            </span>
                                                        )}

                                                    </div>


                                                    {score !== null && (
                                                        <div className="recommendation-bar">

                                                            <div
                                                                className="recommendation-bar-fill"
                                                                style={{
                                                                    width: `${score}%`
                                                                }}
                                                            />

                                                        </div>
                                                    )}

                                                </div>


                                                {isSelected && (
                                                    <span className="recommendation-selected">
                                                        ✓
                                                    </span>
                                                )}

                                            </button>
                                        );
                                    })}

                            </div>


                            <div className="recommendation-note">
                                Select a role below to discover live
                                opportunities.
                            </div>

                        </div>
                    )}

                </div>


                {/* =================================================
                    LIVE JOB CTA
                ================================================= */}

                {hasRecommendations && (
                    <div className="live-job-selector-box">

                        <div className="live-job-selector-content">

                            <span className="live-job-kicker">
                                Live Job Search
                            </span>

                            <h3>
                                Find jobs for your target role
                            </h3>

                            <p>
                                Choose a recommendation or search
                                for another role.
                            </p>

                        </div>


                        <button
                            type="button"
                            className="choose-role-button"
                            onClick={openRoleSelector}
                            disabled={loadingJobs}
                        >
                            {loadingJobs
                                ? `Finding Jobs${loadingDots}`
                                : "Choose a Role"}
                        </button>

                    </div>
                )}


                {/* =================================================
                    LIVE JOBS
                ================================================= */}

                {liveJobs.length > 0 && (
                    <div className="live-jobs-wrapper">

                        <LiveJobs
                            jobs={liveJobs}
                            resumeText={resumeText}
                        />

                    </div>
                )}

            </div>


            {/* =====================================================
                ROLE MODAL
            ===================================================== */}

            {showRoleModal && (
                <div
                    className="role-modal-overlay"
                    onClick={closeRoleSelector}
                >

                    <div
                        className="role-modal"
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                    >

                        <div className="role-modal-header">

                            <div>

                                <span className="role-modal-kicker">
                                    Target Role
                                </span>

                                <h2>
                                    Choose the role you want to search
                                </h2>

                                <p>
                                    Select an AI recommendation or
                                    enter another role.
                                </p>

                            </div>


                            <button
                                type="button"
                                className="role-modal-close"
                                onClick={closeRoleSelector}
                                disabled={loadingJobs}
                                aria-label="Close"
                            >
                                ×
                            </button>

                        </div>


                        {/* RECOMMENDED ROLES */}

                        {hasRecommendations && (
                            <div className="role-section">

                                <h3>
                                    Recommended Roles
                                </h3>

                                <div className="role-options">

                                    {recommendations
                                        .slice(0, 5)
                                        .map((item, index) => {

                                            const role =
                                                getRecommendationLabel(
                                                    item
                                                );

                                            if (!role) {
                                                return null;
                                            }

                                            const isSelected =
                                                selectedRole === role;

                                            return (
                                                <button
                                                    type="button"
                                                    className={`role-option ${
                                                        isSelected
                                                            ? "selected"
                                                            : ""
                                                    }`}
                                                    key={`${role}-${index}`}
                                                    onClick={() =>
                                                        handleRecommendedRoleSelect(
                                                            role
                                                        )
                                                    }
                                                    disabled={loadingJobs}
                                                >

                                                    <span className="role-option-number">
                                                        {index + 1}
                                                    </span>

                                                    <span className="role-option-name">
                                                        {role}
                                                    </span>

                                                    {isSelected && (
                                                        <span className="role-option-check">
                                                            ✓
                                                        </span>
                                                    )}

                                                </button>
                                            );
                                        })}

                                </div>

                            </div>
                        )}


                        {/* MANUAL ROLE */}

                        <div className="role-section">

                            <h3>
                                Or search another role
                            </h3>

                            <input
                                type="text"
                                value={manualRole}
                                onChange={handleManualRoleChange}
                                placeholder="e.g. Data Analyst"
                                className="manual-role-input"
                                disabled={loadingJobs}
                            />

                        </div>


                        {/* SELECTED ROLE */}

                        {(selectedRole || manualRole.trim()) && (
                            <div className="selected-role-preview">

                                <span>
                                    Searching for
                                </span>

                                <strong>
                                    {manualRole.trim() ||
                                        selectedRole.trim()}
                                </strong>

                            </div>
                        )}


                        {error && (
                            <div className="modal-error">
                                {error}
                            </div>
                        )}


                        {/* ACTIONS */}

                        <div className="role-modal-actions">

                            <button
                                type="button"
                                className="role-cancel-button"
                                onClick={closeRoleSelector}
                                disabled={loadingJobs}
                            >
                                Cancel
                            </button>


                            <button
                                type="button"
                                className="role-continue-button"
                                onClick={handleRoleContinue}
                                disabled={
                                    loadingJobs ||
                                    (
                                        !selectedRole &&
                                        !manualRole.trim()
                                    )
                                }
                            >
                                {loadingJobs
                                    ? `Finding Jobs${loadingDots}`
                                    : "Find Live Jobs"}
                            </button>

                        </div>

                    </div>
                </div>
            )}

        </section>
    );
}

export default UploadResume;