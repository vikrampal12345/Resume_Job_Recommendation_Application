import "./Navbar.css";
import logo from "../../assets/syncronal-logo.png";
function Navbar() {

    return (

        <nav className="navbar">

            <div className="logo">

                <div className="brand">

                    <img
                        src={logo}
                        alt="Syncronal"
                        className="brand-logo"
                    />

                    <h2>AI Resume Analyzer</h2>

                </div>

            </div>

            <div className="tagline">

                AI Powered Career Recommendation

            </div>

        </nav>

    );

}

export default Navbar;