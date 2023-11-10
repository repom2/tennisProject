import React from 'react';
import { MyComponent } from "/app/src/components/Player/players"
import {Route, Routes} from "react-router-dom"


function App() {

  return (
  <>
    <div className="App">
      <header className="App-header">
        <p>
          Welcome to the <code>React</code> app!
        </p>
      </header>
    </div>
    <Routes>
        <Route path="/*" element='app' />
    </Routes>
    <MyComponent />
    </>
  );
}

export default App;
