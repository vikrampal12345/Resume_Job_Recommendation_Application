import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../../services/api";
import "./Login.css";

import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

const Login = () => {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // ================= INPUT CHANGE =================

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });

    setError("");
  };

  // ================= LOGIN =================

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    const { email, password } = formData;

    // Basic validation
    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    try {
      setIsLoading(true);

      // Send login request to FastAPI
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
      });

      console.log("Login response:", data);

      // ================= SAVE JWT TOKEN =================

      if (!data.token) {
        throw new Error("Login successful but no authentication token was received.");
      }

      localStorage.setItem("syncronalToken", data.token);

      // ================= SAVE USER =================

      if (data.user) {
        localStorage.setItem(
          "syncronalUser",
          JSON.stringify(data.user)
        );
      }

      // ================= LOGIN STATE =================

      localStorage.setItem(
  "syncronalUser",
  JSON.stringify(data.user)
);
      // Clear any old analysis data
      localStorage.removeItem("syncronalResumeAnalysis");
      localStorage.removeItem("syncronalResumeText");
      localStorage.removeItem("syncronalResumeFileName");

      // ================= REDIRECT =================

      navigate("/dashboard", { replace: true });

    } catch (error) {
      console.error("Login failed:", error);

      setError(
        error.message || "Invalid email or password. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">

      {/* ================= NAVBAR ================= */}

      <header className="login-navbar">
        <div className="login-navbar-inner">

          {/* Logo */}

          <Link to="/" className="login-logo-wrapper">

            <div className="login-logo-icon">
              <span>S</span>
            </div>

            <span className="login-logo">
              SYNCRONAL
            </span>

          </Link>

          {/* Signup */}

          <div className="login-signup-wrapper">

            <span className="login-signup-text">
              Don't have an account?
            </span>

            <Link
              to="/signup"
              className="login-signup-button"
            >
              Sign Up
            </Link>

          </div>

        </div>
      </header>


      {/* ================= MAIN ================= */}

      <main className="login-main">

        {/* Decorative background */}

        <div className="login-decoration login-decoration-blue"></div>

        <div className="login-decoration login-decoration-purple"></div>


        <div className="login-container">


          {/* ================= LEFT CONTENT ================= */}

          <section className="login-left">

            <div className="login-badge">
              <Sparkles size={16} />
              <span>AI Powered Career Platform</span>
            </div>


            <h1 className="login-heading">
              Welcome
              <br />

              <span>
                Back to SYNCRONAL
              </span>
            </h1>


            <p className="login-description">
              Continue your AI-powered career journey.
              Analyze your resume, discover relevant jobs
              and identify the skills you need to grow.
            </p>


            {/* Benefits */}

            <div className="login-benefits">

              <div className="login-benefit">

                <div className="login-benefit-icon blue">
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h3>
                    Smart Resume Analysis
                  </h3>

                  <p>
                    Get AI-powered insights from your resume.
                  </p>
                </div>

              </div>


              <div className="login-benefit">

                <div className="login-benefit-icon green">
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h3>
                    Personalized Recommendations
                  </h3>

                  <p>
                    Find jobs that match your skills and profile.
                  </p>
                </div>

              </div>


              <div className="login-benefit">

                <div className="login-benefit-icon purple">
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h3>
                    Track Your Career Growth
                  </h3>

                  <p>
                    Improve your skills with personalized insights.
                  </p>
                </div>

              </div>

            </div>

          </section>


          {/* ================= LOGIN FORM ================= */}

          <section className="login-form-section">

            <div className="login-form-card">


              {/* Header */}

              <div className="login-form-header">

                <div className="login-user-icon">
                  <Lock size={27} />
                </div>

                <h2 className="login-title">
                  Welcome Back
                </h2>

                <p className="login-subtitle">
                  Log in to continue your career journey
                </p>

              </div>


              {/* Error */}

              {error && (
                <div className="login-error">
                  {error}
                </div>
              )}


              {/* Form */}

              <form
                onSubmit={handleSubmit}
                className="login-form"
              >


                {/* ================= EMAIL ================= */}

                <div className="login-field">

                  <label>
                    Email Address
                  </label>

                  <div className="login-input-wrapper">

                    <Mail
                      className="login-input-icon"
                      size={19}
                    />

                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      className="login-input"
                      autoComplete="email"
                      disabled={isLoading}
                    />

                  </div>

                </div>


                {/* ================= PASSWORD ================= */}

                <div className="login-field">

                  <div className="login-password-label">

                    <label>
                      Password
                    </label>

                    <Link
                      to="/forgot-password"
                      className="login-forgot-link"
                    >
                      Forgot Password?
                    </Link>

                  </div>


                  <div className="login-input-wrapper">

                    <Lock
                      className="login-input-icon"
                      size={19}
                    />

                    <input
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Enter your password"
                      className="login-input login-password-input"
                      autoComplete="current-password"
                      disabled={isLoading}
                    />


                    <button
                      type="button"
                      className="login-password-toggle"
                      onClick={() =>
                        setShowPassword(!showPassword)
                      }
                      disabled={isLoading}
                    >

                      {showPassword ? (
                        <EyeOff size={19} />
                      ) : (
                        <Eye size={19} />
                      )}

                    </button>

                  </div>

                </div>


                {/* ================= REMEMBER ME ================= */}

                <div className="login-remember">

                  <label>

                    <input
                      type="checkbox"
                      disabled={isLoading}
                    />

                    <span>
                      Remember me
                    </span>

                  </label>

                </div>


                {/* ================= SUBMIT ================= */}

                <button
                  type="submit"
                  className="login-submit"
                  disabled={isLoading}
                >

                  <span>
                    {isLoading ? "Logging In..." : "Log In"}
                  </span>

                  {!isLoading && (
                    <ArrowRight size={18} />
                  )}

                </button>

              </form>


              {/* Security */}

              <div className="login-security">

                <ShieldCheck size={16} />

                <span>
                  Your information is securely protected
                </span>

              </div>


              {/* Signup */}

              <div className="login-bottom-signup">

                <p>
                  Don't have an account?{" "}

                  <Link to="/signup">
                    Create Account
                  </Link>
                </p>

              </div>

            </div>

          </section>

        </div>

      </main>


      {/* ================= FOOTER ================= */}

      <footer className="login-footer">

        © {new Date().getFullYear()} SYNCRONAL.
        AI-powered career guidance.

      </footer>

    </div>
  );
};

export default Login;