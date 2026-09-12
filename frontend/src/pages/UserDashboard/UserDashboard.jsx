import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  FileText,
  Briefcase,
  Send,
  Bookmark,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Clock3,
  XCircle,
  Target,
  Sparkles,
  Upload,
  Search,
  Brain,
  UserRound,
} from "lucide-react";

import Navbar from "../../components/Navbar/Navbar";
import { apiRequest } from "../../services/api";
import "./UserDashboard.css";

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const savedUser = localStorage.getItem("syncronalUser");
  const user = savedUser ? JSON.parse(savedUser) : null;
  const userName = user?.name || "Pradyuman";

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await apiRequest("/dashboard/");

        console.log("Dashboard data:", data);
        setDashboard(data);
      } catch (error) {
        console.error("Dashboard error:", error);
        setError(error.message || "Unable to load dashboard.");
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  // Backend field names can vary, so keep the existing UI values as
  // fallbacks until the exact /dashboard/ response is finalized.
  const resumeScore =
    dashboard?.resume_score ??
    dashboard?.resumeScore ??
    dashboard?.latest_resume?.score ??
    85;

  const jobsMatched =
    dashboard?.jobs_matched ??
    dashboard?.jobsMatched ??
    dashboard?.matched_jobs ??
    24;

  const applications =
    dashboard?.applications ??
    dashboard?.application_count ??
    dashboard?.applications_count ??
    12;

  const savedJobs =
    dashboard?.saved_jobs ??
    dashboard?.savedJobs ??
    dashboard?.saved_jobs_count ??
    8;

  const atsScore =
    dashboard?.ats_score ??
    dashboard?.atsScore ??
    dashboard?.latest_resume?.ats_score ??
    91;

  const skillsDetected =
    dashboard?.skills_detected ??
    dashboard?.skillsDetected ??
    dashboard?.latest_resume?.skills_detected ??
    18;

  const skillGaps =
    dashboard?.skill_gaps ??
    dashboard?.skillGaps ??
    dashboard?.latest_resume?.skill_gaps ??
    4;

  const applicationStats = dashboard?.application_stats || {};

  const appliedCount =
    applicationStats.applied ??
    dashboard?.applied_count ??
    12;

  const interviewCount =
    applicationStats.interview ??
    applicationStats.interviews ??
    dashboard?.interview_count ??
    3;

  const reviewCount =
    applicationStats.review ??
    applicationStats.under_review ??
    dashboard?.review_count ??
    5;

  const rejectedCount =
    applicationStats.rejected ??
    dashboard?.rejected_count ??
    4;

  if (loading) {
    return (
      <div className="dashboard-page">
        <Navbar />
        <main className="dashboard-main">

         {error && (
           <div
             role="alert"
             style={{
               marginBottom: "16px",
               padding: "12px 16px",
               borderRadius: "10px",
               background: "rgba(239, 68, 68, 0.08)",
               border: "1px solid rgba(239, 68, 68, 0.2)",
               color: "#b91c1c",
             }}
           >
             {error}
           </div>
         )}
          <section className="dashboard-header">
            <div>
              <span className="dashboard-label">CAREER DASHBOARD</span>
              <h1>Loading your dashboard...</h1>
              <p>Fetching your latest career data.</p>
            </div>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="dashboard-page">

      {/* ================= NAVBAR ================= */}
      <Navbar />


      {/* ================= MAIN ================= */}
      <main className="dashboard-main">

        {/* ================= HEADER ================= */}

        <section className="dashboard-header">

          <div>
            <span className="dashboard-label">
              CAREER DASHBOARD
            </span>

            <h1>
              Welcome back, {userName}! 👋
            </h1>

            <p>
              Here's an overview of your resume, job opportunities
              and career progress.
            </p>
          </div>


          <Link
            to="/analyze"
            className="dashboard-primary-button"
          >
            <Upload size={18} />
            Analyze Resume
            <ArrowRight size={17} />
          </Link>

        </section>


        {/* ================= OVERVIEW CARDS ================= */}

        <section className="overview-grid">

          {/* Resume Score */}
          <div className="overview-card">

            <div className="overview-card-top">

              <div className="overview-icon blue">
                <FileText size={21} />
              </div>

              <span className="overview-trend positive">
                <TrendingUp size={13} />
                5%
              </span>

            </div>

            <span className="overview-title">
              Resume Score
            </span>

            <strong className="overview-number">
              85%
            </strong>

            <span className="overview-subtitle">
              Improved this week
            </span>

          </div>


          {/* Jobs Matched */}
          <div className="overview-card">

            <div className="overview-card-top">

              <div className="overview-icon green">
                <Briefcase size={21} />
              </div>

              <span className="overview-trend positive">
                <TrendingUp size={13} />
                6
              </span>

            </div>

            <span className="overview-title">
              Jobs Matched
            </span>

            <strong className="overview-number">
              24
            </strong>

            <span className="overview-subtitle">
              New matches available
            </span>

          </div>


          {/* Applications */}
          <div className="overview-card">

            <div className="overview-card-top">

              <div className="overview-icon purple">
                <Send size={21} />
              </div>

              <span className="overview-trend neutral">
                This week
              </span>

            </div>

            <span className="overview-title">
              Applications
            </span>

            <strong className="overview-number">
              12
            </strong>

            <span className="overview-subtitle">
              3 applications this week
            </span>

          </div>


          {/* Saved Jobs */}
          <div className="overview-card">

            <div className="overview-card-top">

              <div className="overview-icon orange">
                <Bookmark size={21} />
              </div>

              <span className="overview-trend neutral">
                Saved
              </span>

            </div>

            <span className="overview-title">
              Saved Jobs
            </span>

            <strong className="overview-number">
              8
            </strong>

            <span className="overview-subtitle">
              Jobs in your shortlist
            </span>

          </div>

        </section>


        {/* ================= MAIN DASHBOARD GRID ================= */}

        <section className="dashboard-grid">


          {/* ================= RESUME ANALYSIS ================= */}

          <div className="dashboard-card resume-card">

            <div className="card-header">

              <div>
                <h2>Resume Analysis</h2>

                <p>
                  Latest analysis of your resume
                </p>
              </div>

              <Link to="/analyze">
                View Details
                <ArrowRight size={15} />
              </Link>

            </div>


            <div className="resume-analysis-content">

              <div className="dashboard-score-circle">

                <div className="score-inner">

                  <strong>{resumeScore}</strong>

                  <span>%</span>

                </div>

                <small>
                  Resume Score
                </small>

              </div>


              <div className="resume-metrics">

                <div className="metric-row">

                  <div className="metric-info">
                    <span>ATS Compatibility</span>
                    <strong>{atsScore}%</strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      className="metric-fill blue-fill"
                      style={{ width: `${Math.min(Number(atsScore) || 0, 100)}%` }}
                    ></div>
                  </div>

                </div>


                <div className="metric-row">

                  <div className="metric-info">
                    <span>Skills Detected</span>
                    <strong>{skillsDetected}</strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      className="metric-fill green-fill"
                      style={{ width: "78%" }}
                    ></div>
                  </div>

                </div>


                <div className="metric-row">

                  <div className="metric-info">
                    <span>Experience</span>
                    <strong>Good</strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      className="metric-fill purple-fill"
                      style={{ width: "84%" }}
                    ></div>
                  </div>

                </div>


                <div className="metric-row">

                  <div className="metric-info">
                    <span>Skill Gaps</span>
                    <strong>{skillGaps}</strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      className="metric-fill orange-fill"
                      style={{ width: "35%" }}
                    ></div>
                  </div>

                </div>

              </div>

            </div>


            <div className="resume-checks">

              <div>
                <CheckCircle2 size={16} />
                <span>Contact Information</span>
              </div>

              <div>
                <CheckCircle2 size={16} />
                <span>Skills Section</span>
              </div>

              <div>
                <CheckCircle2 size={16} />
                <span>Work Experience</span>
              </div>

              <div className="check-warning">
                <AlertCircle size={16} />
                <span>Projects Section</span>
              </div>

            </div>

          </div>


          {/* ================= SKILL GAP ================= */}

          <div className="dashboard-card skill-card">

            <div className="card-header">

              <div>
                <h2>Skill Gap Analysis</h2>

                <p>
                  Skills you should improve
                </p>
              </div>

              <Link to="/skill-analysis">
                View All
                <ArrowRight size={15} />
              </Link>

            </div>


            <div className="skills-list">

              <div className="skill-row">

                <div className="skill-name">
                  <span>TypeScript</span>
                  <strong>52%</strong>
                </div>

                <div className="skill-bar">
                  <div
                    className="skill-progress orange"
                    style={{ width: "52%" }}
                  ></div>
                </div>

              </div>


              <div className="skill-row">

                <div className="skill-name">
                  <span>AWS</span>
                  <strong>41%</strong>
                </div>

                <div className="skill-bar">
                  <div
                    className="skill-progress purple"
                    style={{ width: "41%" }}
                  ></div>
                </div>

              </div>


              <div className="skill-row">

                <div className="skill-name">
                  <span>System Design</span>
                  <strong>35%</strong>
                </div>

                <div className="skill-bar">
                  <div
                    className="skill-progress red"
                    style={{ width: "35%" }}
                  ></div>
                </div>

              </div>


              <div className="skill-row">

                <div className="skill-name">
                  <span>Docker</span>
                  <strong>30%</strong>
                </div>

                <div className="skill-bar">
                  <div
                    className="skill-progress blue"
                    style={{ width: "30%" }}
                  ></div>
                </div>

              </div>

            </div>


            <div className="skill-message">

              <Brain size={17} />

              <p>
                Improving <strong>TypeScript</strong> and
                <strong> System Design</strong> could increase
                your job match score.
              </p>

            </div>

          </div>

        </section>


        {/* ================= AI INSIGHT ================= */}

        <section className="ai-insight">

          <div className="ai-insight-icon">
            <Sparkles size={23} />
          </div>

          <div className="ai-insight-content">

            <span>
              AI CAREER INSIGHT
            </span>

            <h3>
              Your resume is strong in frontend development.
            </h3>

            <p>
              Adding TypeScript projects and cloud experience
              could improve your match with software engineering
              roles.
            </p>

          </div>

          <Link
            to="/skill-analysis"
            className="ai-insight-button"
          >
            Improve Skills
            <ArrowRight size={16} />
          </Link>

        </section>


        {/* ================= RECOMMENDED JOBS ================= */}

        <section className="dashboard-card jobs-card">

          <div className="card-header">

            <div>
              <h2>Recommended Jobs</h2>

              <p>
                Opportunities matching your profile
              </p>
            </div>

            <Link to="/jobs">
              View All Jobs
              <ArrowRight size={15} />
            </Link>

          </div>


          <div className="jobs-table">

            {/* Job 1 */}
            <div className="job-row">

              <div className="company-logo">
                G
              </div>

              <div className="job-info">

                <strong>
                  Frontend Developer
                </strong>

                <span>
                  Google • Bengaluru • Hybrid
                </span>

              </div>

              <div className="job-skills">
                <span>React</span>
                <span>JavaScript</span>
                <span>TypeScript</span>
              </div>

              <div className="match-score">
                92% Match
              </div>

              <button className="apply-button">
                Apply
              </button>

            </div>


            {/* Job 2 */}
            <div className="job-row">

              <div className="company-logo microsoft">
                M
              </div>

              <div className="job-info">

                <strong>
                  Software Engineer
                </strong>

                <span>
                  Microsoft • Hyderabad • Hybrid
                </span>

              </div>

              <div className="job-skills">
                <span>React</span>
                <span>Node.js</span>
                <span>SQL</span>
              </div>

              <div className="match-score">
                88% Match
              </div>

              <button className="apply-button">
                Apply
              </button>

            </div>


            {/* Job 3 */}
            <div className="job-row">

              <div className="company-logo amazon">
                A
              </div>

              <div className="job-info">

                <strong>
                  Full Stack Developer
                </strong>

                <span>
                  Amazon • Bengaluru • On-site
                </span>

              </div>

              <div className="job-skills">
                <span>React</span>
                <span>Node.js</span>
                <span>AWS</span>
              </div>

              <div className="match-score">
                85% Match
              </div>

              <button className="apply-button">
                Apply
              </button>

            </div>

          </div>

        </section>


        {/* ================= BOTTOM GRID ================= */}

        <section className="bottom-grid">


          {/* ================= APPLICATIONS ================= */}

          <div className="dashboard-card applications-card">

            <div className="card-header">

              <div>
                <h2>Application Overview</h2>

                <p>
                  Track your job applications
                </p>
              </div>

              <Link to="/applications">
                View All
                <ArrowRight size={15} />
              </Link>

            </div>


            <div className="application-stats">

              <div>
                <span className="application-dot blue-dot"></span>
                <strong>12</strong>
                <small>Applied</small>
              </div>

              <div>
                <span className="application-dot purple-dot"></span>
                <strong>3</strong>
                <small>Interview</small>
              </div>

              <div>
                <span className="application-dot orange-dot"></span>
                <strong>5</strong>
                <small>Review</small>
              </div>

              <div>
                <span className="application-dot red-dot"></span>
                <strong>4</strong>
                <small>Rejected</small>
              </div>

            </div>


            <div className="application-progress">

              <div style={{ width: "50%" }}></div>
              <div style={{ width: "12.5%" }}></div>
              <div style={{ width: "20%" }}></div>
              <div style={{ width: "17.5%" }}></div>

            </div>

          </div>


          {/* ================= RECENT APPLICATIONS ================= */}

          <div className="dashboard-card recent-card">

            <div className="card-header">

              <div>
                <h2>Recent Applications</h2>

                <p>
                  Your latest activity
                </p>
              </div>

              <Link to="/applications">
                All
                <ArrowRight size={15} />
              </Link>

            </div>


            <div className="recent-list">

              <div className="recent-item">

                <div className="recent-company">
                  G
                </div>

                <div>
                  <strong>
                    Google
                  </strong>

                  <span>
                    Software Engineer
                  </span>
                </div>

                <span className="status review">
                  Under Review
                </span>

              </div>


              <div className="recent-item">

                <div className="recent-company microsoft">
                  M
                </div>

                <div>
                  <strong>
                    Microsoft
                  </strong>

                  <span>
                    Frontend Developer
                  </span>
                </div>

                <span className="status interview">
                  Interview
                </span>

              </div>


              <div className="recent-item">

                <div className="recent-company amazon">
                  A
                </div>

                <div>
                  <strong>
                    Amazon
                  </strong>

                  <span>
                    SDE Intern
                  </span>
                </div>

                <span className="status applied">
                  Applied
                </span>

              </div>

            </div>

          </div>

        </section>


        {/* ================= QUICK ACTIONS ================= */}

        <section className="quick-actions-section">

          <div className="quick-actions-header">

            <div>
              <span>
                QUICK ACTIONS
              </span>

              <h2>
                Continue Your Career Journey
              </h2>
            </div>

          </div>


          <div className="quick-actions-grid">

            <Link
              to="/analyze"
              className="action-card"
            >
              <div className="action-icon blue">
                <Upload size={21} />
              </div>

              <div>
                <strong>
                  Analyze Resume
                </strong>

                <span>
                  Get fresh AI insights
                </span>
              </div>

              <ArrowRight size={17} />

            </Link>


            <Link
              to="/jobs"
              className="action-card"
            >
              <div className="action-icon green">
                <Search size={21} />
              </div>

              <div>
                <strong>
                  Explore Jobs
                </strong>

                <span>
                  Find matching opportunities
                </span>
              </div>

              <ArrowRight size={17} />

            </Link>


            <Link
              to="/skill-analysis"
              className="action-card"
            >
              <div className="action-icon purple">
                <Brain size={21} />
              </div>

              <div>
                <strong>
                  Improve Skills
                </strong>

                <span>
                  Work on your skill gaps
                </span>
              </div>

              <ArrowRight size={17} />

            </Link>


            <Link
              to="/profile"
              className="action-card"
            >
              <div className="action-icon orange">
                <UserRound size={21} />
              </div>

              <div>
                <strong>
                  Update Profile
                </strong>

                <span>
                  Keep your profile complete
                </span>
              </div>

              <ArrowRight size={17} />

            </Link>

          </div>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer className="dashboard-footer">

        <p>
          © {new Date().getFullYear()} SYNCRONAL.
          AI-powered career guidance.
        </p>

        <div>
          <Link to="/how-it-works">
            How It Works
          </Link>

          <Link to="/privacy">
            Privacy
          </Link>

          <Link to="/terms">
            Terms
          </Link>
        </div>

      </footer>

    </div>
  );
}

export default Dashboard;