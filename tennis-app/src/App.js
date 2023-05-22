import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState(0);
  const [currentDate, setCurrentDate] = useState(0);
  useEffect(() => {
  fetch(' http://0.0.0.0:8000/tennisapi/players').then(res => res.json()).then(data => {
      console.log('joo');
    });
  }, []);
  return (
    <div className="App">
      <header className="App-header">
      <p>The date is </p> <br/>

      </header>
    </div>
  );
}

export default App;

