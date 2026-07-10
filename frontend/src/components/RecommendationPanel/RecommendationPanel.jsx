import "./RecommendationPanel.css";
import RecommendationCard from "../RecommendationCard/RecommendationCard";

function RecommendationPanel({ recommendations }) {

    if (!recommendations || recommendations.length === 0) {
        return null;
    }

    return (
        <section className="recommendation-panel">

            <h2>AI Recommended Roles</h2>

            <div className="recommendation-list">

                {recommendations.map((recommendation, index) => (

                    <RecommendationCard
                        key={index}
                        recommendation={recommendation}
                    />

                ))}

            </div>

        </section>
    );

}

export default RecommendationPanel;