const CurrentStats = ({ currentSeasonStats }) => {
  const leagues = Object.keys(currentSeasonStats);

  if (leagues.length === 0) return null;

  return (
    <div className="current-stats-container">
      {leagues.map((league) => (
        <div key={league} className="league-stats">
          <div className="league-header">
            <h3 className="league-title">{league}</h3>
            <div className="basic-stats">
              <div className="stat-item">
                <span className="stat-value">
                  {currentSeasonStats[league].matches}
                </span>
                <span className="stat-label">Matches</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {Math.round(currentSeasonStats[league].minutes / 90)}
                </span>
                <span className="stat-label">90s</span>
              </div>
            </div>
          </div>

          <div className="detailed-stats">
            <div className="stats-group goals">
              <div className="stat-box">
                <span className="stat-value">
                  {currentSeasonStats[league].goals}
                </span>
                <span className="stat-label">Goals</span>
              </div>
              <div className="stat-box">
                <span className="stat-value">
                  {currentSeasonStats[league].expected_goals}
                </span>
                <span className="stat-label">xG</span>
              </div>
            </div>

            <div className="stats-group assists">
              <div className="stat-box">
                <span className="stat-value">
                  {currentSeasonStats[league].assists}
                </span>
                <span className="stat-label">Assists</span>
              </div>
              <div className="stat-box">
                <span className="stat-value">
                  {currentSeasonStats[league].expected_assists}
                </span>
                <span className="stat-label">xA</span>
              </div>
            </div>

            <div className="stats-group actions">
              <div className="stat-box">
                <span className="stat-value">
                  {currentSeasonStats[league].shot_creating_actions}
                </span>
                <span className="stat-label">Shot Actions</span>
              </div>
              <div className="stat-box">
                <span className="stat-value">
                  {currentSeasonStats[league].goal_creating_actions}
                </span>
                <span className="stat-label">Goal Actions</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CurrentStats;
