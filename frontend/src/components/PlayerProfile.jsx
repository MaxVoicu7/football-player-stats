import { useState } from "react";
import "../styles/PlayerProfile.css";
import "../styles/PlayerCard.css";
import "../styles/CurrentStats.css";
import CurrentStats from "./CurrentStats";

const PlayerCard = ({ generalInfo }) => {
  // Only truncate if really necessary (longer names)
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

const PlayerProfile = ({
  generalInfo,
  currentSeasonStats,
  scoutingReport,
  showAnalysis,
  playerOverview,
}) => {
  return (
    <div className="player-profile">
      <PlayerCard generalInfo={generalInfo} />
      <CurrentStats currentSeasonStats={currentSeasonStats} />
      <div className="scouting-report">
        <h3>Scouting Report</h3>
        <div className="stats-grid">
          {scoutingReport.map((stat, index) => (
            <div key={index} className="stat-item">
              <span className="stat-label">{stat.stat}</span>
              <span className="stat-value">
                {stat.per_90} (Top {stat.percentile}%)
              </span>
            </div>
          ))}
        </div>
      </div>
      {showAnalysis && playerOverview && (
        <div className="analysis-section">
          <h3>Expert Analysis</h3>
          {/* Add the analysis components here */}
          {/* This section will be implemented in the next iteration */}
        </div>
      )}
    </div>
  );
};

export default PlayerProfile;
