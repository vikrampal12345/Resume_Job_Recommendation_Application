import React, { useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  Upload,
  FileText,
  X,
  Sparkles,
  Brain,
  Target,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Briefcase,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react";

import Navbar from "../../components/Navbar/Navbar";
import "./Analyze.css";

function Analyze() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [jobRole, setJobRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = (file) => {
    if (!file) return;

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
    ];

    if (!allowedTypes.includes(file.type)) {
      alert("Please upload a PDF or DOC/DOCX file.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("File size should be less than 5MB.");
      return;
    }

    setSelectedFile(file);
    setShowResults(false);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);

    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const removeFile = () => {
    setSelectedFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleAnalyze = () => {
    if (!selectedFile) {
      alert("Please upload your resume first.");
      return;
    }

    if (!jobRole.trim()) {
      alert("Please enter your target job role.");
      return;
    }

    setIsAnalyzing(true);

    // Demo analysis
    // Replace this with your backend API call later.
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowResults(true);
    }, 1800);
  };

  return (
    <div className="analyze-page">
      <Navbar />

      <main className="analyze-container">

        {/* Header */}
        <section className="analyze-header">
          <div>
            <div className="page-badge">
              <Sparkles size={16} />
              AI Resume Analysis
            </div>

            <h1>
              Analyze Your Resume
              <span> with AI</span>
            </h1>

            <p>
              Upload your resume and let SYNCRONAL analyze your skills,
              experience, ATS compatibility, and career opportunities.
            </p>
          </div>

          <div className="header-icon">
            <Brain size={42} />
          </div>
        </section>

        {/* Main Analysis Card */}
        <section className="analysis-workspace">

          {/* Upload Section */}
          <div className="upload-section">

            <div className="section-title">
              <div className="title-icon">
                <Upload size={20} />
              </div>

              <div>
                <h2>Upload Your Resume</h2>
                <p>PDF or DOCX • Maximum 5MB</p>
              </div>
            </div>

            {!selectedFile ? (
              <div
                className={`drop-zone ${dragActive ? "drag-active" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  hidden
                />

                <div className="upload-icon">
                  <Upload size={30} />
                </div>

                <h3>Drop your resume here</h3>

                <p>
                  or <span>browse files</span> from your computer
                </p>

                <small>
                  Supported formats: PDF, DOC, DOCX
                </small>
              </div>
            ) : (
              <div className="selected-file">

                <div className="file-info">
                  <div className="file-icon">
                    <FileText size={28} />
                  </div>

                  <div>
                    <h3>{selectedFile.name}</h3>

                    <p>
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <button
                  className="remove-file"
                  onClick={removeFile}
                  type="button"
                >
                  <X size={18} />
                </button>

              </div>
            )}

          </div>

          {/* Job Target Section */}
          <div className="job-section">

            <div className="section-title">
              <div className="title-icon">
                <Target size={20} />
              </div>

              <div>
                <h2>Target Job</h2>
                <p>Tell us what role you're targeting</p>
              </div>
            </div>

            <div className="form-group">
              <label>
                Target Job Role <span>*</span>
              </label>

              <div className="input-wrapper">
                <Briefcase size={19} />

                <input
                  type="text"
                  placeholder="e.g. Frontend Developer"
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>
                Job Description
                <span className="optional">Optional</span>
              </label>

              <textarea
                placeholder="Paste the job description here for a more accurate analysis..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows="6"
              />

              <div className="textarea-footer">
                <span>
                  Adding a job description improves the accuracy of the
                  analysis.
                </span>

                <span>
                  {jobDescription.length} characters
                </span>
              </div>
            </div>

          </div>

          {/* Analyze Button */}
          <div className="analyze-action">

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <span className="spinner"></span>
                  Analyzing Resume...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Analyze My Resume
                  <ArrowRight size={20} />
                </>
              )}
            </button>

            <p>
              <ShieldCheck size={15} />
              Your resume is securely processed for analysis.
            </p>

          </div>

        </section>

        {/* Results */}
        {showResults && (
          <section className="results-section">

            <div className="results-header">
              <div>
                <div className="page-badge">
                  <CheckCircle2 size={16} />
                  Analysis Complete
                </div>

                <h2>Your Resume Analysis</h2>

                <p>
                  Here's how your resume performs for{" "}
                  <strong>{jobRole}</strong>.
                </p>
              </div>
            </div>

            {/* Score Cards */}
            <div className="score-grid">

              <div className="score-card main-score">
                <div className="score-circle">
                  <strong>85</strong>
                  <span>/100</span>
                </div>

                <div>
                  <h3>Resume Score</h3>
                  <p>Good resume with room for improvement</p>
                </div>
              </div>

              <div className="score-card">
                <div className="result-card-icon">
                  <TrendingUp size={22} />
                </div>

                <h3>ATS Score</h3>
                <strong>91%</strong>
                <p>Excellent ATS compatibility</p>
              </div>

              <div className="score-card">
                <div className="result-card-icon">
                  <Target size={22} />
                </div>

                <h3>Job Match</h3>
                <strong>88%</strong>
                <p>Strong match for target role</p>
              </div>

            </div>

            {/* Analysis Details */}
            <div className="results-grid">

              <div className="result-panel">
                <div className="panel-heading">
                  <CheckCircle2 size={21} />
                  <h3>Strengths</h3>
                </div>

                <ul>
                  <li>Strong technical skills section</li>
                  <li>Clear project descriptions</li>
                  <li>Good use of industry keywords</li>
                  <li>Well-structured resume format</li>
                </ul>
              </div>

              <div className="result-panel warning-panel">
                <div className="panel-heading">
                  <AlertCircle size={21} />
                  <h3>Areas to Improve</h3>
                </div>

                <ul>
                  <li>Add more measurable achievements</li>
                  <li>Improve professional summary</li>
                  <li>Add missing target-role keywords</li>
                  <li>Strengthen experience descriptions</li>
                </ul>
              </div>

            </div>

            {/* Skills */}
            <div className="skills-panel">

              <div className="panel-heading">
                <Zap size={21} />
                <h3>Skill Analysis</h3>
              </div>

              <div className="skills-content">

                <div className="skill-column">
                  <h4>Detected Skills</h4>

                  <div className="skill-tags">
                    <span>React</span>
                    <span>JavaScript</span>
                    <span>HTML</span>
                    <span>CSS</span>
                    <span>Node.js</span>
                    <span>Git</span>
                  </div>
                </div>

                <div className="skill-column">
                  <h4>Recommended Skills</h4>

                  <div className="skill-tags recommended">
                    <span>TypeScript</span>
                    <span>AWS</span>
                    <span>Docker</span>
                    <span>System Design</span>
                  </div>
                </div>

              </div>

            </div>

            {/* CTA */}
            <div className="results-cta">

              <div>
                <h3>Want to improve your career score?</h3>

                <p>
                  Explore recommended jobs and identify the skills you
                  should develop next.
                </p>
              </div>

              <div className="cta-buttons">
                <Link to="/dashboard" className="secondary-button">
                  View Dashboard
                </Link>

                <Link to="/jobs" className="primary-button">
                  Explore Jobs
                  <ArrowRight size={18} />
                </Link>
              </div>

            </div>

          </section>
        )}

        {/* Features */}
        {!showResults && (
          <section className="features-section">

            <div className="features-header">
              <h2>What SYNCRONAL Analyzes</h2>

              <p>
                Get a complete understanding of your resume and career
                readiness.
              </p>
            </div>

            <div className="features-grid">

              <div className="feature-card">
                <div className="feature-icon">
                  <Target size={23} />
                </div>

                <h3>Resume Score</h3>

                <p>
                  Get an overall score based on structure, content,
                  skills and relevance.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <Briefcase size={23} />
                </div>

                <h3>Job Match</h3>

                <p>
                  See how well your resume matches your target job
                  requirements.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <Brain size={23} />
                </div>

                <h3>Skill Analysis</h3>

                <p>
                  Identify your existing skills and discover important
                  skills you're missing.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <TrendingUp size={23} />
                </div>

                <h3>Career Insights</h3>

                <p>
                  Receive AI-powered recommendations to improve your
                  career opportunities.
                </p>
              </div>

            </div>

          </section>
        )}

      </main>
    </div>
  );
}

export default Analyze;