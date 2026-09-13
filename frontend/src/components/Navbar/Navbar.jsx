import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  Home,
  FileSearch,
  LayoutDashboard,
  CircleHelp,
  Sun,
  Moon,
  ChevronDown,
} from "lucide-react";

import "./Navbar.css";
import logo from "../../assets/syncronal-logo.png";

function Navbar() {
  const navigate = useNavigate();

  const [darkMode, setDarkMode] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // ================= USER DATA =================

  const storedUser = localStorage.getItem("syncronalUser");

  let user = {};

  try {
    user = storedUser ? JSON.parse(storedUser) : {};
  } catch (error) {
    console.error("Failed to read user data:", error);
    user = {};
  }

  const userName = user?.name || "Pradyuman Singh";
  // Show only first letter of user's name
  const userInitial = userName
    .trim()
    .charAt(0)
    .toUpperCase();

  // ================= HOW IT WORKS =================

  const handleHowItWorks = () => {
    // If user is not on Home page
    if (window.location.pathname !== "/home") {
      navigate("/home");

      // Wait for Home page to render
      setTimeout(() => {
        const section = document.getElementById("how-it-works");

        if (section) {
          section.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      }, 300);

      return;
    }

    // If already on Home page
    const section = document.getElementById("how-it-works");

    if (section) {
      section.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  // ================= LOGOUT =================

  const handleLogout = () => {
    // Remove authentication data
    localStorage.removeItem("syncronalToken");
    localStorage.removeItem("syncronalUser");
    localStorage.removeItem("syncronalLoggedIn");

    // Remove temporary resume/analysis data
    localStorage.removeItem("syncronalResumeText");
    localStorage.removeItem("syncronalResumeAnalysis");
    localStorage.removeItem("syncronalResumeFileName");
    localStorage.removeItem("syncronalTargetJobRole");
    localStorage.removeItem("syncronalTargetJobDescription");

    // IMPORTANT:
    // Do NOT remove syncronalProfile
    // because profile details should remain saved.

    // Close dropdown
    setShowUserMenu(false);

    // Redirect to login
    navigate("/login", { replace: true });
  };

  // ================= DARK MODE =================

  const toggleDarkMode = () => {
    setDarkMode((prev) => {
      const newMode = !prev;

      if (newMode) {
        document.body.classList.add("dark-mode");
      } else {
        document.body.classList.remove("dark-mode");
      }

      return newMode;
    });
  };

  return (
    <nav className="navbar">

      {/* ================= LEFT - BRAND ================= */}

      <div className="navbar-left">

        <Link to="/home" className="brand">

          <img
            src={logo}
            alt="Syncronal"
            className="brand-logo"
          />

          <div className="brand-text">
            <h2>AI Powered Career Recommendation</h2>
          </div>

        </Link>

      </div>


      {/* ================= CENTER - NAVIGATION ================= */}

      <div className="navbar-center">

        {/* Home */}

        <Link to="/home" className="nav-link active">
          <Home size={18} />
          <span>Home</span>
        </Link>


        {/* Analyze */}

        <Link to="/analyze" className="nav-link">
          <FileSearch size={18} />
          <span>Analyze</span>
        </Link>


        {/* Dashboard */}

        <Link to="/dashboard" className="nav-link">
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </Link>


        {/* How It Works */}
        <Link
          to="/home#how-it-works"
          className="nav-link"
          onClick={(e) => {
            // If already on Home page, prevent navigation
            // and scroll directly to the section
            if (window.location.pathname === "/home") {
              e.preventDefault();

              const section = document.getElementById("how-it-works");

              if (section) {
                section.scrollIntoView({
                  behavior: "smooth",
                  block: "start",
                });
              }
            }
          }}
        >
          <CircleHelp size={18} />
          <span>How It Works</span>
        </Link>

      </div>


      {/* ================= RIGHT - USER ================= */}

      <div className="navbar-right">

        {/* Dark / Light Mode */}

        <button
          className="theme-toggle"
          onClick={toggleDarkMode}
          aria-label="Toggle dark mode"
          type="button"
        >
          {darkMode ? (
            <Sun size={20} />
          ) : (
            <Moon size={20} />
          )}
        </button>


        {/* User */}

        <div className="user-wrapper">

          <button
            className="user-profile"
            onClick={() =>
              setShowUserMenu((prev) => !prev)
            }
            type="button"
          >

            {/* First letter only */}

            <div className="user-avatar">
              {userInitial}
            </div>

            {/* User name */}

            <span className="user-name">
              {userName}
            </span>

            <ChevronDown
              size={18}
              className={`user-arrow ${showUserMenu ? "rotate" : ""
                }`}
            />

          </button>


          {/* ================= USER DROPDOWN ================= */}

          {showUserMenu && (

            <div className="user-dropdown">

              <Link
                to="/profile"
                onClick={() =>
                  setShowUserMenu(false)
                }
              >
                My Profile
              </Link>


              <Link
                to="/settings"
                onClick={() =>
                  setShowUserMenu(false)
                }
              >
                Settings
              </Link>


              <button
                type="button"
                onClick={handleLogout}
              >
                Logout
              </button>

            </div>

          )}

        </div>

      </div>

    </nav>
  );
}

export default Navbar;