import { useState } from "react";
import "../styles/PlayerSearch.css";
import "../styles/NeonLoader.css";
import NeonLoader from "./NeonLoader";
import PlayerProfile from "./PlayerProfile";

const PlayerSearch = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchStatus, setSearchStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [playerData, setPlayerData] = useState(null);
  const [showAnalysis, setShowAnalysis] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setIsLoading(true);
    setSearchStatus("");
    setShowAnalysis(false);

    try {
      const response = await fetch(
        `http://localhost:8000/api/player/search?name=${encodeURIComponent(
          searchTerm.trim()
        )}`
      );
      const data = await response.json();

      if (data.success) {
        setPlayerData(data.data);
        setSearchStatus("success");
      } else {
        setPlayerData(null);
        setSearchStatus("error");
      }
    } catch (error) {
      console.error("Error:", error);
      setSearchStatus("error");
      setPlayerData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSearchTerm("");
    setIsLoading(false);
    setSearchStatus("");
    setPlayerData(null);
    setShowAnalysis(false);
  };

  const handleAnalyze = () => {
    setShowAnalysis(true);
  };

  const showClearButton = searchTerm.trim() || showAnalysis;

  return (
    <div className="search-section">
      <div className="search-wrapper">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search for a player..."
            className="search-input"
            disabled={isLoading}
          />
          <div className="buttons-container">
            <button
              type="submit"
              className={`search-button ${
                !searchTerm.trim() ? "disabled" : ""
              }`}
              disabled={isLoading || !searchTerm.trim()}
            >
              {isLoading ? "Searching..." : "Search"}
            </button>
            <button
              type="button"
              onClick={handleClear}
              className={`clear-button ${!showClearButton ? "disabled" : ""}`}
              disabled={isLoading || !showClearButton}
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {playerData && (
        <div className="stats-container">
          <div className="stats-content">
            <PlayerProfile
              generalInfo={playerData.general_info}
              currentSeasonStats={playerData.current_season_stats}
              scoutingReport={playerData.scouting_report}
              showAnalysis={showAnalysis}
              playerOverview={showAnalysis ? playerData.player_overview : null}
            />
          </div>
          {!showAnalysis && (
            <div className="analyze-button-container">
              <button className="analyze-button" onClick={handleAnalyze}>
                Analyze Player
              </button>
            </div>
          )}
        </div>
      )}

      {searchStatus === "error" && (
        <div className="error-container">
          <p className="error-message">
            Connection error: Failed to find player
          </p>
        </div>
      )}
    </div>
  );
};

export default PlayerSearch;
