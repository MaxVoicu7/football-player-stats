import "./App.css";
import PlayerSearch from "./components/PlayerSearch";

function App() {
  return (
    <div className="app">
      <h1 className="main-title">Football Player Stats</h1>
      <div className="search-container">
        <div className="search-box">
          <p className="search-description">
            Enter a player&apos;s name to discover detailed statistics and
            analysis
          </p>
          <PlayerSearch />
        </div>
      </div>
    </div>
  );
}

export default App;
