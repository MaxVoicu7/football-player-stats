import { useState } from "react";
import "../styles/PlayerProfile.css";

const PlayerProfile = ({
  generalInfo,
  currentSeasonStats,
  scoutingReport,
  showAnalysis,
  playerOverview,
}) => {
  return (
    <div className="player-profile">
      {/* Basic Info Section - Always visible */}
      <div className="basic-info-section">
        <div className="player-header">
          <img
            src={generalInfo.photo_url}
            alt={generalInfo.name}
            className="player-photo"
          />
          <div className="player-info">
            <h2>{generalInfo.name}</h2>
            <p>Age: {generalInfo.age}</p>
            <p>Club: {generalInfo.club}</p>
            <p>Position: {generalInfo.position}</p>
            <p>National Team: {generalInfo.national_team}</p>
          </div>
        </div>

        <div className="current-stats">
          <h3>Current Season Stats</h3>
          {/* Display MLS stats */}
          {currentSeasonStats.MLS && (
            <div className="stats-grid">
              {Object.entries(currentSeasonStats.MLS).map(([key, value]) => (
                <div key={key} className="stat-item">
                  <span className="stat-label">{key.replace(/_/g, " ")}</span>
                  <span className="stat-value">{value}</span>
                </div>
              ))}
            </div>
          )}
        </div>

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
      </div>

      {/* Analysis Section - Only visible when showAnalysis is true */}
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
