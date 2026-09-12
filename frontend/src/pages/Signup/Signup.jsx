import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../../services/api";
import "./Signup.css";

import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

const Signup = () => {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { name, email, password, confirmPassword } = formData;

    setError("");

    // Validation
    if (!name || !email || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      // Send data to FastAPI
      const data = await apiRequest("/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          name,
          email,
          password,
          confirmPassword,
        }),
      });

      console.log("Signup successful:", data);

      // Store JWT token
      if (data.token) {
        localStorage.setItem("syncronalToken", data.token);
      }

      // Store user information
      if (data.user) {
        localStorage.setItem(
          "syncronalUser",
          JSON.stringify(data.user)
        );
      } else {
        localStorage.setItem(
          "syncronalUser",
          JSON.stringify({
            name,
            email,
          })
        );
      }

      localStorage.setItem("syncronalLoggedIn", "true");

      // Redirect
      navigate("/dashboard");

    } catch (error) {
      console.error("Signup failed:", error);

      setError(
        error.message || "Signup failed. Please try again."
      );
    }
  };

  return (
    <div className="signup-page">

      {/* ================= NAVBAR ================= */}
      <header className="signup-navbar">
        <div className="signup-navbar-inner">

          {/* Logo */}
          <Link to="/" className="signup-logo-wrapper">
            <div className="signup-logo-icon">
              <span>S</span>
            </div>

            <span className="signup-logo">
              SYNCRONAL
            </span>
          </Link>

          {/* Login */}
          <div className="signup-login-wrapper">
            <span className="signup-login-text">
              Already have an account?
            </span>

            <Link
              to="/login"
              className="signup-login-button"
            >
              Log In
            </Link>
          </div>

        </div>
      </header>


      {/* ================= MAIN ================= */}
      <main className="signup-main">

        {/* Background decorations */}
        <div className="signup-decoration signup-decoration-blue"></div>
        <div className="signup-decoration signup-decoration-purple"></div>


        <div className="signup-container">

          {/* ================= LEFT CONTENT ================= */}
          <section className="signup-left">

            <div className="signup-badge">
              <Sparkles size={16} />
              <span>AI Powered Career Platform</span>
            </div>

            <h1 className="signup-heading">
              Build Your
              <br />

              <span>
                Career With AI
              </span>
            </h1>

            <p className="signup-description">
              Create your SYNCRONAL account and unlock personalized
              resume analysis, job recommendations and skill gap insights.
            </p>


            {/* Benefits */}
            <div className="signup-benefits">

              {/* Benefit 1 */}
              <div className="signup-benefit">
                <div className="signup-benefit-icon blue">
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h3>
                    AI Resume Analysis
                  </h3>

                  <p>
                    Understand your resume strengths and weaknesses.
                  </p>
                </div>
              </div>


              {/* Benefit 2 */}
              <div className="signup-benefit">
                <div className="signup-benefit-icon green">
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h3>
                    Personalized Job Matches
                  </h3>

                  <p>
                    Discover roles that match your skills and experience.
                  </p>
                </div>
              </div>


              {/* Benefit 3 */}
              <div className="signup-benefit">
                <div className="signup-benefit-icon purple">
                  <CheckCircle2 size={22} />
                </div>

                <div>
                  <h3>
                    Identify Skill Gaps
                  </h3>

                  <p>
                    Know exactly what skills you need to improve.
                  </p>
                </div>
              </div>

            </div>

          </section>


          {/* ================= SIGNUP FORM ================= */}
          <section className="signup-form-section">

            <div className="signup-form-card">

              {/* Form Header */}
              <div className="signup-form-header">

                <div className="signup-user-icon">
                  <User size={28} />
                </div>

                <h2 className="signup-title">
                  Create Account
                </h2>

                <p className="signup-subtitle">
                  Start your AI-powered career journey
                </p>

              </div>


              {/* Error */}
              {error && (
                <div className="signup-error">
                  {error}
                </div>
              )}


              {/* Form */}
              <form
                onSubmit={handleSubmit}
                className="signup-form"
              >

                {/* ================= NAME ================= */}
                <div className="signup-field">

                  <label>
                    Full Name
                  </label>

                  <div className="signup-input-wrapper">

                    <User className="signup-input-icon" size={19} />

                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="Enter your full name"
                      className="signup-input"
                    />

                  </div>

                </div>


                {/* ================= EMAIL ================= */}
                <div className="signup-field">

                  <label>
                    Email Address
                  </label>

                  <div className="signup-input-wrapper">

                    <Mail className="signup-input-icon" size={19} />

                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      className="signup-input"
                    />

                  </div>

                </div>


                {/* ================= PASSWORD ================= */}
                <div className="signup-field">

                  <label>
                    Password
                  </label>

                  <div className="signup-input-wrapper">

                    <Lock className="signup-input-icon" size={19} />

                    <input
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Create a password"
                      className="signup-input signup-password-input"
                    />

                    <button
                      type="button"
                      className="signup-password-toggle"
                      onClick={() =>
                        setShowPassword(!showPassword)
                      }
                    >
                      {showPassword ? (
                        <EyeOff size={19} />
                      ) : (
                        <Eye size={19} />
                      )}
                    </button>

                  </div>

                  <p className="signup-hint">
                    Minimum 8 characters
                  </p>

                </div>


                {/* ================= CONFIRM PASSWORD ================= */}
                <div className="signup-field">

                  <label>
                    Confirm Password
                  </label>

                  <div className="signup-input-wrapper">

                    <Lock className="signup-input-icon" size={19} />

                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="Confirm your password"
                      className="signup-input signup-password-input"
                    />

                    <button
                      type="button"
                      className="signup-password-toggle"
                      onClick={() =>
                        setShowConfirmPassword(
                          !showConfirmPassword
                        )
                      }
                    >
                      {showConfirmPassword ? (
                        <EyeOff size={19} />
                      ) : (
                        <Eye size={19} />
                      )}
                    </button>

                  </div>

                </div>


                {/* ================= TERMS ================= */}
                <div className="signup-terms">

                  <input
                    type="checkbox"
                    required
                  />

                  <p>
                    I agree to the{" "}
                    <Link to="/terms">
                      Terms of Service
                    </Link>{" "}
                    and{" "}
                    <Link to="/privacy">
                      Privacy Policy
                    </Link>
                    .
                  </p>

                </div>


                {/* ================= SUBMIT ================= */}
                <button
                  type="submit"
                  className="signup-submit"
                >
                  <span>Create Account</span>
                  <ArrowRight size={18} />
                </button>

              </form>


              {/* Security */}
              <div className="signup-security">
                <ShieldCheck size={16} />
                <span>
                  Your information is securely protected
                </span>
              </div>


              {/* Login */}
              <div className="signup-bottom-login">

                <p>
                  Already have an account?{" "}

                  <Link to="/login">
                    Log in
                  </Link>
                </p>

              </div>

            </div>

          </section>

        </div>

      </main>


      {/* ================= FOOTER ================= */}
      <footer className="signup-footer">
        © {new Date().getFullYear()} SYNCRONAL.
        AI-powered career guidance.
      </footer>

    </div>
  );
};

export default Signup;