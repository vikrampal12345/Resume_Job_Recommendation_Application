import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Upload,
  Search,
  Brain,
  Target,
  FileText,
  Briefcase,
  TrendingUp,
  CheckCircle2,
  Sparkles,
  BarChart3,
  Zap,
} from "lucide-react";

import Navbar from "../../components/Navbar/Navbar";
import "./Home.css";

function Home() {
  return (
    <div className="home-page">

      {/* ================= NAVBAR ================= */}
      <Navbar />


      {/* ================= HERO SECTION ================= */}
      <main>

        <section className="home-hero">

          <div className="hero-content">

            <div className="hero-badge">
              <Sparkles size={16} />
              <span>AI Powered Career Platform</span>
            </div>

            <h1>
              Build Your Career
              <br />
              <span>Smarter With AI.</span>
            </h1>

            <p className="hero-description">
              Analyze your resume, discover matching jobs, identify
              your skill gaps, and get personalized career insights
              with SYNCRONAL.
            </p>

            <div className="hero-buttons">

              <Link
                to="/analyze"
                className="primary-button"
              >
                <Upload size={19} />
                Analyze My Resume
                <ArrowRight size={18} />
              </Link>

              <Link
                to="/jobs"
                className="secondary-button"
              >
                <Search size={18} />
                Explore Jobs
              </Link>

            </div>

            <div className="hero-trust">

              <div>
                <CheckCircle2 size={17} />
                <span>AI Resume Analysis</span>
              </div>

              <div>
                <CheckCircle2 size={17} />
                <span>Personalized Recommendations</span>
              </div>

              <div>
                <CheckCircle2 size={17} />
                <span>Skill Gap Detection</span>
              </div>

            </div>

          </div>


          {/* ================= RESUME PREVIEW ================= */}

          <div className="hero-visual">

            <div className="analysis-card">

              <div className="analysis-card-header">

                <div className="analysis-title">

                  <div className="analysis-icon">
                    <FileText size={21} />
                  </div>

                  <div>
                    <h3>Resume Analysis</h3>
                    <span>AI generated insights</span>
                  </div>

                </div>

                <div className="analysis-status">
                  <span></span>
                  Analyzed
                </div>

              </div>


              <div className="score-section">

                <div className="score-circle">
                  <div>
                    <strong>85</strong>
                    <small>%</small>
                  </div>
                  <span>Resume Score</span>
                </div>


                <div className="score-details">

                  <div className="score-item">
                    <span>ATS Compatibility</span>
                    <strong>91%</strong>
                  </div>

                  <div className="score-progress">
                    <div
                      className="progress-fill"
                      style={{ width: "91%" }}
                    ></div>
                  </div>


                  <div className="score-item">
                    <span>Skills Detected</span>
                    <strong>18</strong>
                  </div>

                  <div className="score-progress">
                    <div
                      className="progress-fill"
                      style={{ width: "78%" }}
                    ></div>
                  </div>


                  <div className="score-item">
                    <span>Skill Gaps</span>
                    <strong>4</strong>
                  </div>

                  <div className="score-progress">
                    <div
                      className="progress-fill warning"
                      style={{ width: "35%" }}
                    ></div>
                  </div>

                </div>

              </div>


              <div className="analysis-checks">

                <div>
                  <CheckCircle2 size={17} />
                  <span>Contact Information</span>
                </div>

                <div>
                  <CheckCircle2 size={17} />
                  <span>Skills Section</span>
                </div>

                <div>
                  <CheckCircle2 size={17} />
                  <span>Work Experience</span>
                </div>

                <div>
                  <CheckCircle2 size={17} />
                  <span>Education Details</span>
                </div>

              </div>


              <Link
                to="/analyze"
                className="analysis-button"
              >
                View Full Analysis
                <ArrowRight size={17} />
              </Link>

            </div>


            {/* Floating match card */}

            <div className="floating-match">

              <div className="floating-icon">
                <Target size={19} />
              </div>

              <div>
                <span>Best Job Match</span>
                <strong>92% Match</strong>
              </div>

            </div>

          </div>

        </section>


        {/* ================= QUICK ACTIONS ================= */}

        <section className="quick-section">

          <div className="section-heading">

            <div>
              <span className="section-label">GET STARTED</span>

              <h2>Everything You Need to Grow</h2>

              <p>
                Take control of your career with AI-powered tools.
              </p>
            </div>

          </div>


          <div className="quick-grid">

            <Link
              to="/analyze"
              className="quick-card quick-blue"
            >

              <div className="quick-icon">
                <FileText size={24} />
              </div>

              <h3>Analyze Resume</h3>

              <p>
                Upload your resume and get detailed AI-powered
                insights instantly.
              </p>

              <span className="quick-link">
                Start Analysis
                <ArrowRight size={16} />
              </span>

            </Link>


            <Link
              to="/jobs"
              className="quick-card quick-green"
            >

              <div className="quick-icon">
                <Briefcase size={24} />
              </div>

              <h3>Find Jobs</h3>

              <p>
                Discover job opportunities that match your
                skills and experience.
              </p>

              <span className="quick-link">
                Explore Jobs
                <ArrowRight size={16} />
              </span>

            </Link>


            <Link
              to="/skill-analysis"
              className="quick-card quick-purple"
            >

              <div className="quick-icon">
                <Brain size={24} />
              </div>

              <h3>Skill Analysis</h3>

              <p>
                Identify missing skills and understand what
                you need to improve.
              </p>

              <span className="quick-link">
                View Skills
                <ArrowRight size={16} />
              </span>

            </Link>


            <Link
              to="/dashboard"
              className="quick-card quick-orange"
            >

              <div className="quick-icon">
                <BarChart3 size={24} />
              </div>

              <h3>Career Dashboard</h3>

              <p>
                Track applications, saved jobs and your
                overall career progress.
              </p>

              <span className="quick-link">
                Open Dashboard
                <ArrowRight size={16} />
              </span>

            </Link>

          </div>

        </section>


        {/* ================= HOW IT WORKS ================= */}

        <section className="how-section">

          <div className="section-heading centered">

            <span className="section-label">
              SIMPLE PROCESS
            </span>

            <h2>How SYNCRONAL Works</h2>

            <p>
              From your resume to your next career opportunity
              in just a few simple steps.
            </p>

          </div>


          <div className="steps-container">

            <div className="step-card">

              <div className="step-number">
                01
              </div>

              <div className="step-icon">
                <Upload size={24} />
              </div>

              <h3>Upload Resume</h3>

              <p>
                Upload your existing resume and let SYNCRONAL
                understand your professional profile.
              </p>

            </div>


            <div className="step-line"></div>


            <div className="step-card">

              <div className="step-number">
                02
              </div>

              <div className="step-icon">
                <Brain size={24} />
              </div>

              <h3>AI Analysis</h3>

              <p>
                Our AI analyzes your skills, experience,
                education and resume structure.
              </p>

            </div>


            <div className="step-line"></div>


            <div className="step-card">

              <div className="step-number">
                03
              </div>

              <div className="step-icon">
                <Target size={24} />
              </div>

              <h3>Get Recommendations</h3>

              <p>
                Discover relevant jobs and understand how
                well they match your profile.
              </p>

            </div>


            <div className="step-line"></div>


            <div className="step-card">

              <div className="step-number">
                04
              </div>

              <div className="step-icon">
                <TrendingUp size={24} />
              </div>

              <h3>Grow Your Career</h3>

              <p>
                Identify skill gaps and take action to become
                more job-ready.
              </p>

            </div>

          </div>

        </section>


        {/* ================= CAREER INSIGHTS ================= */}

        <section className="insights-section">

          <div className="insights-content">

            <span className="section-label">
              YOUR CAREER
            </span>

            <h2>
              Know Where You Stand.
              <br />
              Know What to Improve.
            </h2>

            <p>
              SYNCRONAL turns your resume into actionable career
              insights so you can make better decisions about
              your next opportunity.
            </p>

            <Link
              to="/analyze"
              className="insights-button"
            >
              Analyze My Resume
              <ArrowRight size={18} />
            </Link>

          </div>


          <div className="insights-stats">

            <div className="insight-stat">

              <div className="stat-icon blue">
                <Zap size={21} />
              </div>

              <div>
                <strong>Resume Score</strong>
                <span>Understand your resume quality</span>
              </div>

            </div>


            <div className="insight-stat">

              <div className="stat-icon purple">
                <Target size={21} />
              </div>

              <div>
                <strong>Job Match</strong>
                <span>Find opportunities that fit you</span>
              </div>

            </div>


            <div className="insight-stat">

              <div className="stat-icon green">
                <TrendingUp size={21} />
              </div>

              <div>
                <strong>Skill Growth</strong>
                <span>Know what skills to improve</span>
              </div>

            </div>

          </div>

        </section>


        {/* ================= FINAL CTA ================= */}

        <section className="home-cta">

          <div className="cta-icon">
            <Sparkles size={26} />
          </div>

          <h2>Ready to Improve Your Career?</h2>

          <p>
            Upload your resume and let SYNCRONAL show you
            what to do next.
          </p>

          <Link
            to="/analyze"
            className="cta-button"
          >
            Analyze My Resume
            <ArrowRight size={19} />
          </Link>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer className="home-footer">
        <p>
          © {new Date().getFullYear()} SYNCRONAL.
          AI-powered career guidance.
        </p>

        <div className="footer-links">
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

export default Home;