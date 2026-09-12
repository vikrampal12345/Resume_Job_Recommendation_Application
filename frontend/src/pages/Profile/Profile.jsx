import React, { useState } from "react";
import {
  UserRound,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  GraduationCap,
  Edit3,
  Save,
  FileText,
  CheckCircle2,
  Plus,
  X,
} from "lucide-react";

import Navbar from "../../components/Navbar/Navbar";
import "./Profile.css";

function Profile() {
  const [isEditing, setIsEditing] = useState(false);

  const [profile, setProfile] = useState({
    name: "Pradyuman Singh",
    email: "pradyuman@example.com",
    phone: "+91 98765 43210",
    location: "Greater Noida, India",
    role: "Frontend Developer",
    education: "B.Tech Computer Science",
    experience: "Fresher",
    bio: "Passionate developer interested in building modern web applications and AI-powered solutions.",
  });

  const [skills, setSkills] = useState([
    "React",
    "JavaScript",
    "HTML",
    "CSS",
    "Node.js",
    "Git",
  ]);

  const [newSkill, setNewSkill] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setProfile((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const addSkill = () => {
    const skill = newSkill.trim();

    if (!skill) return;

    if (!skills.includes(skill)) {
      setSkills([...skills, skill]);
    }

    setNewSkill("");
  };

  const removeSkill = (skillToRemove) => {
    setSkills(
      skills.filter((skill) => skill !== skillToRemove)
    );
  };

  const handleSave = () => {
    localStorage.setItem(
      "syncronalProfile",
      JSON.stringify({
        ...profile,
        skills,
      })
    );

    setIsEditing(false);
  };

  return (
    <div className="profile-page">
      <Navbar />

      <main className="profile-container">

        {/* PAGE HEADER */}
        <section className="profile-page-header">
          <div>
            <div className="profile-badge">
              <UserRound size={16} />
              My Profile
            </div>

            <h1>Profile Settings</h1>

            <p>
              Manage your personal information, skills and career
              preferences.
            </p>
          </div>

          <button
            className="edit-profile-btn"
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit3 size={17} />

            {isEditing ? "Cancel Editing" : "Edit Profile"}
          </button>
        </section>

        {/* PROFILE CARD */}
        <section className="profile-card">

          <div className="profile-cover"></div>

          <div className="profile-main">

            <div className="profile-avatar">
              PS
            </div>

            <div className="profile-main-info">
              <h2>{profile.name}</h2>

              <p>{profile.role}</p>

              <div className="profile-meta">
                <span>
                  <MapPin size={15} />
                  {profile.location}
                </span>

                <span>
                  <Mail size={15} />
                  {profile.email}
                </span>
              </div>
            </div>

            <div className="profile-status">
              <CheckCircle2 size={17} />
              Profile Complete
            </div>

          </div>

        </section>

        {/* PERSONAL INFORMATION */}
        <section className="profile-section">

          <div className="section-heading">
            <div className="section-heading-icon">
              <UserRound size={20} />
            </div>

            <div>
              <h2>Personal Information</h2>
              <p>Your basic personal details</p>
            </div>
          </div>

          <div className="form-grid">

            <div className="form-group">
              <label>Full Name</label>

              <div className="input-box">
                <UserRound size={17} />

                <input
                  type="text"
                  name="name"
                  value={profile.name}
                  onChange={handleChange}
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Email Address</label>

              <div className="input-box">
                <Mail size={17} />

                <input
                  type="email"
                  name="email"
                  value={profile.email}
                  onChange={handleChange}
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Phone Number</label>

              <div className="input-box">
                <Phone size={17} />

                <input
                  type="tel"
                  name="phone"
                  value={profile.phone}
                  onChange={handleChange}
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Location</label>

              <div className="input-box">
                <MapPin size={17} />

                <input
                  type="text"
                  name="location"
                  value={profile.location}
                  onChange={handleChange}
                  disabled={!isEditing}
                />
              </div>
            </div>

          </div>

        </section>

        {/* PROFESSIONAL INFORMATION */}
        <section className="profile-section">

          <div className="section-heading">
            <div className="section-heading-icon">
              <Briefcase size={20} />
            </div>

            <div>
              <h2>Professional Information</h2>
              <p>Information about your career</p>
            </div>
          </div>

          <div className="form-grid">

            <div className="form-group">
              <label>Current / Target Role</label>

              <div className="input-box">
                <Briefcase size={17} />

                <input
                  type="text"
                  name="role"
                  value={profile.role}
                  onChange={handleChange}
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Experience</label>

              <select
                name="experience"
                value={profile.experience}
                onChange={handleChange}
                disabled={!isEditing}
              >
                <option>Fresher</option>
                <option>0-1 Years</option>
                <option>1-3 Years</option>
                <option>3-5 Years</option>
                <option>5+ Years</option>
              </select>
            </div>

            <div className="form-group full-width">
              <label>Education</label>

              <div className="input-box">
                <GraduationCap size={17} />

                <input
                  type="text"
                  name="education"
                  value={profile.education}
                  onChange={handleChange}
                  disabled={!isEditing}
                />
              </div>
            </div>

            <div className="form-group full-width">
              <label>About You</label>

              <textarea
                name="bio"
                value={profile.bio}
                onChange={handleChange}
                disabled={!isEditing}
                rows="5"
              />
            </div>

          </div>

        </section>

        {/* SKILLS */}
        <section className="profile-section">

          <div className="section-heading">
            <div className="section-heading-icon">
              <CheckCircle2 size={20} />
            </div>

            <div>
              <h2>Skills</h2>
              <p>Add skills that represent your expertise</p>
            </div>
          </div>

          <div className="skills-container">

            {skills.map((skill) => (
              <div className="skill-tag" key={skill}>
                {skill}

                {isEditing && (
                  <button
                    type="button"
                    onClick={() => removeSkill(skill)}
                  >
                    <X size={13} />
                  </button>
                )}
              </div>
            ))}

          </div>

          {isEditing && (
            <div className="add-skill">

              <input
                type="text"
                placeholder="Add a skill..."
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    addSkill();
                  }
                }}
              />

              <button
                type="button"
                onClick={addSkill}
              >
                <Plus size={17} />
                Add Skill
              </button>

            </div>
          )}

        </section>

        {/* RESUME */}
        <section className="profile-section resume-section">

          <div className="section-heading">
            <div className="section-heading-icon">
              <FileText size={20} />
            </div>

            <div>
              <h2>Resume</h2>
              <p>Your latest uploaded resume</p>
            </div>
          </div>

          <div className="resume-card">

            <div className="resume-icon">
              <FileText size={25} />
            </div>

            <div className="resume-info">
              <h3>My_Resume.pdf</h3>
              <p>Last analyzed recently • Resume Score: 85%</p>
            </div>

            <button className="view-resume-btn">
              View Resume
            </button>

          </div>

        </section>

        {/* SAVE BUTTON */}
        {isEditing && (
          <div className="save-container">

            <button
              className="save-profile-btn"
              onClick={handleSave}
            >
              <Save size={18} />
              Save Changes
            </button>

          </div>
        )}

      </main>
    </div>
  );
}

export default Profile;