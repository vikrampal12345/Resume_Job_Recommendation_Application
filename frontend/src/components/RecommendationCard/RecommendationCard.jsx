import "./RecommendationCard.css";

function RecommendationCard({ recommendation }) {

    const rankEmoji = {
        1: "",
        2: "",
        3: "",
        4: "",
        5: ""
    };

    return (

        <div className="recommendation-card">

            {/* <div className="card-header">

                <span className="rank-badge">

                    {rankEmoji[recommendation.rank]}

                    {" "}#{recommendation.rank}

                </span>

            </div> */}

            <h3>{recommendation.job_role}</h3>

            <div className="progress-bar">

                <div
                    className="progress-fill"
                    style={{
                        width: `${recommendation.confidence}%`
                    }}
                ></div>

            </div>

            <p className="match-score">

                AI Match • {recommendation.confidence}%

            </p>

        </div>

    );

}

export default RecommendationCard;