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

// Helper function to categorize stats
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
  showAnalysis,
  playerOverview,
}) => {
  return (
    <div className="player-profile">
      <PlayerCard generalInfo={generalInfo} />
      <CurrentStats currentSeasonStats={currentSeasonStats} />
      <ScoutingReport scoutingReport={scoutingReport} />
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
