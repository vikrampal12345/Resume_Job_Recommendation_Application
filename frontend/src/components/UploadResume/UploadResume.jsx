import "./UploadResume.css";
import { useState, useRef } from "react";
import {
    uploadResume,
    fetchLiveJobs
} from "../../services/resumeService";

import RecommendationPanel from "../RecommendationPanel/RecommendationPanel";
import LiveJobs from "../LiveJobs/LiveJobs";
import Loader from "../Loader/Loader";

function UploadResume() {

    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [liveJobs, setLiveJobs] = useState([]);
    const [loadingJobs, setLoadingJobs] = useState(false);
    const fileInputRef = useRef(null);
    const [errorMessage, setErrorMessage] = useState("");

   function handleFileChange(event) {

        const file = event.target.files[0];

        if (!file) return;

        const allowedTypes = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ];

        if (!allowedTypes.includes(file.type)) {

            setErrorMessage("Please upload a PDF or DOCX resume.");

            event.target.value = "";

            return;

        }

        const maxSize = 10 * 1024 * 1024; // 10 MB

        if (file.size > maxSize) {

            setErrorMessage("File size must be less than 10 MB.");

            event.target.value = "";

            return;

        }
        setErrorMessage("");
        setSelectedFile(file);

    }

    async function analyzeResume() {

        if (!selectedFile) {

            setErrorMessage("Please select a resume.");
            return;

        }

        try {

            setLoading(true);
            setErrorMessage("");

            const prediction = await uploadResume(selectedFile);

            setRecommendations(prediction.recommendations);

            // Start loading live jobs
            setLoadingJobs(true);

            const jobs = await fetchLiveJobs(
                prediction.recommendations
            );

            setLiveJobs(jobs.jobs);

            setLoadingJobs(false);

        }

        catch (error) {

            console.error(error);

            if (error.response) {

                alert("Resume analysis failed. Please try another resume.");

            }

            else if (error.request) {

                alert("Unable to connect to the server. Please check your internet connection.");

            }

            else {

                alert("Something went wrong. Please try again.");

            }

        }

        finally {

            setLoading(false);

        }

    }

    return (

        <section className="upload-section">

            <div
                className={
                    recommendations.length > 0
                        ? "analysis-layout"
                        : "upload-layout"
                }
            >

                {/* Upload Panel */}

                <div className="upload-panel">

                    <label className="upload-box">

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.docx,.doc"
                            onChange={handleFileChange}
                            hidden
                        />

                        <div className="upload-icon">

                            📄

                        </div>

                        <h2>Upload Resume</h2>

                        <p className="upload-text">
                            Drag & Drop your resume here
                        </p>

                        <p className="upload-subtext">
                            or click below to browse
                        </p>

                        <button
                            type="button"
                            className="browse-btn"
                            onClick={() => fileInputRef.current.click()}
                        >
                            Browse Files
                        </button>

                        <small>
                            Supported Formats: PDF • DOCX
                        </small>

                    

                        <p className="filename">

                            {selectedFile
                                ? selectedFile.name
                                : "No file selected"}

                        </p>

                        <button
                            className="analyze-btn"
                            onClick={analyzeResume}
                        >

                            {loading
                                ? "Analyzing..."
                                : "Analyze Resume"}

                        </button>

                        {
                            errorMessage && (

                                <div className="error-banner">

                                    {errorMessage}

                                </div>

                            )
                        }
                    </label>    

                </div>

                {/* Recommendation Panel */}

                {

                    recommendations.length > 0 && (

                        <div className="recommendation-panel-wrapper">

                            <RecommendationPanel
                                recommendations={recommendations}
                            />

                        </div>

                    )

                }

            </div>

            {/* Live Jobs */}

            {
                loadingJobs ? (

                    <Loader />

                ) : (

                    <LiveJobs jobs={liveJobs} />

                )
            }

        </section>

    );

}

export default UploadResume;