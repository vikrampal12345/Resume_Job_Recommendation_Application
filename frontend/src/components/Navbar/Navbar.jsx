import { useState } from "react";
import { Link } from "react-router-dom";
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
  const [darkMode, setDarkMode] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

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
        <Link to="/how-it-works" className="nav-link">
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
            onClick={() => setShowUserMenu(!showUserMenu)}
          >

            <div className="user-avatar">
              PS
            </div>

            <span className="user-name">
              Pradyuman Singh
            </span>

            <ChevronDown
              size={18}
              className={`user-arrow ${
                showUserMenu ? "rotate" : ""
              }`}
            />

          </button>


          {/* User Dropdown */}
          {showUserMenu && (
            <div className="user-dropdown">

              <Link to="/profile">
                My Profile
              </Link>

              <Link to="/settings">
                Settings
              </Link>

              <button
                onClick={() => {
                  localStorage.removeItem(
                    "syncronalLoggedIn"
                  );

                  setShowUserMenu(false);
                }}
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