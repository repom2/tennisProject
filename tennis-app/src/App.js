import React, { useState, useEffect } from 'react';
import './App.css';
import {getPlayers} from "data/DataFetch";
import {useGetPlayers} from "hooks";
import { useQuery, QueryClientProvider } from 'react-query'
import queryClient from "./data/queryClient";

function App() {
  const [currentTime, setCurrentTime] = useState(0);
  const [currentDate, setCurrentDate] = useState(0);
  const {data: players} = useGetPlayers();
console.log(players);
  return (

    <div className="App">
      <header className="App-header">
      <p>The date is ret wrongg</p> <br/>
      <p>{players}</p> <br/>

      </header>
    </div>
  );
}

export default App;

