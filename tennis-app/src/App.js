import React, { useState, useEffect } from 'react';
import './App.css';
import {getPlayers} from "data/DataFetch";

function App() {
  const [currentTime, setCurrentTime] = useState(0);
  const [currentDate, setCurrentDate] = useState(0);
  const usegetPlayers = () => {
    return {
        queryFn: () => getPlayers(),
        queryKey: ["PLAYERS"],
    };
};
  return (
    <div className="App">
      <header className="App-header">
      <p>The date is </p> <br/>

      </header>
    </div>
  );
}

export default App;

