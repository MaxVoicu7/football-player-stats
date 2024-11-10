import { useState } from "react";
import "../styles/PlayerSearch.css";
import "../styles/NeonLoader.css";
import NeonLoader from "./NeonLoader";

const PlayerSearch = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchStatus, setSearchStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [showStatsContainer, setShowStatsContainer] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setSearchStatus(null);
    setErrorMessage("");
    setShowStatsContainer(true);

    try {
      const timer = new Promise((resolve) => setTimeout(resolve, 1500));

      const [response] = await Promise.all([
        fetch(
          `http://localhost:8000/api/player/search?name=${encodeURIComponent(
            searchQuery.trim()
          )}`
        ),
        timer,
      ]);

      const data = await response.json();

      if (data.success) {
        setSearchStatus("success");
        console.log("Player data:", data.data);
      } else {
        setSearchStatus("error");
        setErrorMessage(data.error || "Failed to find player");
      }
    } catch (error) {
      console.error("Detailed error:", error);
      setSearchStatus("error");
      setErrorMessage(`Connection error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSearchQuery("");
    setIsLoading(false);
    setSearchStatus(null);
    setErrorMessage("");
    setShowStatsContainer(false);
  };

  const showClearButton = searchQuery.trim() || showStatsContainer;

  return (
    <div className="search-section">
      <div className="search-wrapper">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for a player..."
            className="search-input"
            disabled={isLoading}
          />
          <div className="buttons-container">
            <button
              type="submit"
              className={`search-button ${
                !searchQuery.trim() ? "disabled" : ""
              }`}
              disabled={isLoading || !searchQuery.trim()}
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

      {showStatsContainer && (
        <div className="stats-container">
          {isLoading ? (
            <NeonLoader />
          ) : searchStatus === "success" ? (
            <div className="stats-content">
              <p className="placeholder-text">
                Player stats will be displayed here
              </p>
            </div>
          ) : (
            searchStatus === "error" && (
              <div className="error-container">
                <p className="error-message">{errorMessage}</p>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};

export default PlayerSearch;
