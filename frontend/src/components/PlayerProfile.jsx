import { useState } from "react";
import "../styles/PlayerProfile.css";
import "../styles/PlayerCard.css";
import "../styles/CurrentStats.css";
import CurrentStats from "./CurrentStats";
import NeonLoader from "./NeonLoader";

const PlayerCard = ({ generalInfo }) => {
  const truncateText = (text, maxLength = 25) => {
    return text.length > maxLength
      ? `${text.substring(0, maxLength)}...`
      : text;
  };

  return (
    <div className="player-card">
      <div className="card-header">
        <div className="teams-info">
          <div className="team-container club">
            <span className="team-label" title={generalInfo.club}>
              {truncateText(generalInfo.club)}
            </span>
          </div>
          <div className="team-container national">
            <span className="team-label" title={generalInfo.national_team}>
              {truncateText(generalInfo.national_team)}
            </span>
          </div>
        </div>
      </div>
      <div className="card-image">
        <img src={generalInfo.photo_url} alt={generalInfo.name} />
      </div>
      <div className="card-info">
        <h3 className="player-name">{generalInfo.name}</h3>
        <div className="player-details">
          <div className="details-container">
            <span className="age-label">Age {generalInfo.age}</span>
            <span className="details-divider">•</span>
            <span className="position-label" title={generalInfo.position}>
              {generalInfo.position.split(" ")[0]}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatItem = ({ stat, per90, percentile }) => {
  return (
    <div className={`stat-item ${getStatCategory(stat)}`}>
      <div className="stat-label">{stat}</div>
      <div className="stat-value">
        <span className="stat-number">{per90}</span>
        <div className="percentile-bar">
          <div
            className="percentile-fill"
            style={{ width: `${percentile}%` }}
          />
        </div>
        <span className="percentile-number">{percentile}%</span>
      </div>
    </div>
  );
};

const getStatCategory = (stat) => {
  const attackingStats = ["Goals", "Shots", "xG", "Assists"];
  const possessionStats = ["Passes", "Carries", "Take-Ons", "Touches"];
  const defensiveStats = ["Tackles", "Interceptions", "Blocks", "Clearances"];

  if (attackingStats.some((s) => stat.includes(s))) return "attacking";
  if (possessionStats.some((s) => stat.includes(s))) return "possession";
  if (defensiveStats.some((s) => stat.includes(s))) return "defensive";
  return "";
};

const ScoutingReport = ({ scoutingReport }) => {
  const [selectedStat, setSelectedStat] = useState(null);

  const statCategories = {
    attacking: [
      "Non-Penalty Goals",
      "npxG: Non-Penalty xG",
      "Shots Total",
      "Assists",
      "xAG: Exp. Assisted Goals",
      "npxG + xAG",
      "Shot-Creating Actions",
    ],
    possession: [
      "Passes Attempted",
      "Pass Completion %",
      "Progressive Passes",
      "Progressive Carries",
      "Successful Take-Ons",
      "Touches (Att Pen)",
      "Progressive Passes Rec",
    ],
    defensive: [
      "Tackles",
      "Interceptions",
      "Blocks",
      "Clearances",
      "Aerials Won",
    ],
  };

  return (
    <div className="scouting-report">
      <h3>Scouting Report</h3>
      <div className="stat-categories">
        {Object.entries(statCategories).map(([category, stats]) => (
          <div key={category} className="category">
            <h4 className={`category-title ${category}`}>
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </h4>
            <div className="stat-list">
              {stats.map((stat) => {
                const statData = scoutingReport.find((s) => s.stat === stat);
                return (
                  <div
                    key={stat}
                    className={`stat-item ${
                      selectedStat === stat ? "selected" : ""
                    }`}
                    onClick={() => setSelectedStat(stat)}
                  >
                    <div className="stat-name">{stat}</div>
                    <div className="stat-bar-container">
                      <div className="stat-bar-background"></div>
                      <div
                        className="stat-bar"
                        style={{ width: `${statData?.percentile}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      {selectedStat && (
        <div className="stat-details">
          <h4>{selectedStat}</h4>
          <p>
            Per 90: {scoutingReport.find((s) => s.stat === selectedStat).per_90}
          </p>
          <p>
            Percentile:{" "}
            {scoutingReport.find((s) => s.stat === selectedStat).percentile}%
          </p>
        </div>
      )}
    </div>
  );
};

const PlayerProfile = ({
  generalInfo,
  currentSeasonStats,
  scoutingReport,
  playerOverview,
  onAnalysisToggle,
}) => {
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyzeClick = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowAnalysis(true);
      onAnalysisToggle(true);
    }, 1000);
  };

  return (
    <div className="player-profile">
      <PlayerCard generalInfo={generalInfo} />
      <CurrentStats currentSeasonStats={currentSeasonStats} />
      <ScoutingReport scoutingReport={scoutingReport} />

      {!showAnalysis && !isAnalyzing && (
        <div className="analyze-button-container">
          <button className="analyze-button" onClick={handleAnalyzeClick}>
            Analyze Player
          </button>
        </div>
      )}

      {isAnalyzing && (
        <div className="analysis-loading">
          <NeonLoader />
        </div>
      )}

      {showAnalysis && (
        <div className="analysis-section">
          <h3>Expert Analysis</h3>
          <div className="analysis-content">
            {/* Summary */}
            {playerOverview?.summary && (
              <div className="analysis-category">
                <h4>Summary</h4>
                <p>{playerOverview.summary}</p>
              </div>
            )}

            {playerOverview?.performance_profile && (
              <>
                <div className="analysis-category">
                  <h4>Playing Style</h4>
                  <div className="style-details">
                    <p>
                      Primary Style:{" "}
                      {
                        playerOverview.performance_profile.playing_style
                          ?.primary_style
                      }
                    </p>
                    <p>
                      Secondary Style:{" "}
                      {
                        playerOverview.performance_profile.playing_style
                          ?.secondary_style
                      }
                    </p>
                    <h5>Category Scores</h5>
                    <div className="category-scores">
                      <div className="score-item">
                        <span>
                          Attacking:{" "}
                          {
                            playerOverview.performance_profile.category_scores
                              .attacking.score
                          }
                          /100
                        </span>
                        <span>
                          Contribution:{" "}
                          {playerOverview.performance_profile.category_scores.attacking.contribution.toFixed(
                            2
                          )}
                          %
                        </span>
                      </div>
                      <div className="score-item">
                        <span>
                          Possession:{" "}
                          {
                            playerOverview.performance_profile.category_scores
                              .possession.score
                          }
                          /100
                        </span>
                        <span>
                          Contribution:{" "}
                          {playerOverview.performance_profile.category_scores.possession.contribution.toFixed(
                            2
                          )}
                          %
                        </span>
                      </div>
                      <div className="score-item">
                        <span>
                          Defensive:{" "}
                          {
                            playerOverview.performance_profile.category_scores
                              .defensive.score
                          }
                          /100
                        </span>
                        <span>
                          Contribution:{" "}
                          {playerOverview.performance_profile.category_scores.defensive.contribution.toFixed(
                            2
                          )}
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {playerOverview.performance_profile.key_strengths?.length >
                  0 && (
                  <div className="analysis-category">
                    <h4>Key Strengths</h4>
                    <div className="strength-list">
                      {playerOverview.performance_profile.key_strengths.map(
                        (strength, index) => (
                          <div key={index} className="strength-item">
                            <span className="strength-stat">
                              {strength.stat}
                            </span>
                            <span className="strength-value">
                              Value: {strength.value} (Top {strength.percentile}
                              %)
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {playerOverview.performance_profile.areas_for_improvement
                  ?.length > 0 && (
                  <div className="analysis-category">
                    <h4>Areas for Development</h4>
                    <div className="improvement-list">
                      {playerOverview.performance_profile.areas_for_improvement.map(
                        (area, index) => (
                          <div key={index} className="improvement-item">
                            <span className="improvement-stat">
                              {area.stat}
                            </span>
                            <span className="improvement-value">
                              Current: {area.value} (Bottom{" "}
                              {100 - area.percentile}%)
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </>
            )}

            {playerOverview?.development_analysis && (
              <div className="analysis-category">
                <h4>Development Analysis</h4>
                <p>
                  Development Phase:{" "}
                  {playerOverview.development_analysis.development_timeframe}
                </p>

                {playerOverview.development_analysis.training_recommendations
                  ?.length > 0 && (
                  <div className="training-recommendations">
                    <h5>Training Recommendations</h5>
                    <div className="training-list">
                      {playerOverview.development_analysis.training_recommendations.map(
                        (rec, index) => (
                          <div
                            key={index}
                            className="training-item"
                            data-priority={rec.priority}
                          >
                            <span className="training-focus">
                              {rec.focus_area}
                            </span>
                            <div className="training-details">
                              <p>
                                Priority:{" "}
                                <span className={`priority-${rec.priority}`}>
                                  {rec.priority}
                                </span>
                              </p>
                              <p>Current Level: {rec.current_level}%</p>
                              <p>Target Level: {rec.target_level}%</p>
                              <p>Timeframe: {rec.timeframe}</p>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {playerOverview?.overall_rating && (
              <div className="analysis-category">
                <h4>Overall Rating</h4>
                <div className="rating-display">
                  <span className="rating-number">
                    {playerOverview.overall_rating}
                  </span>
                  <span className="rating-max">/100</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerProfile;
