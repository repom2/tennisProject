import React from 'react';
import { PlayerList } from "/app/src/components/Player/PlayerList"
import { Tips } from "/app/src/components/Tips/Tips"
import { Header } from "./Header/Header"
import {BrowserRouter as Router,Route, Routes} from "react-router-dom"
import Sidebar from './Sidebar/Sidebar';
import './App.css';
import {QueryClientProvider} from "react-query";
import queryClient from "/app/src/data/queryClient";


function App() {

  return (
  <><Router>
        <React.StrictMode>
            <QueryClientProvider client={queryClient}>
    <div className="App">

    </div>
    <Header />
    <div className='appContainer'>
        <Sidebar />
        <Routes>
            <Route path="/elo" element={<PlayerList />} />
            <Route path="/tips" element={<Tips />} />
            {/* ... Add as many routes as needed */}
          </Routes>
    </div>
        </QueryClientProvider>
        </React.StrictMode>
    </Router>
    </>
  );
}

export default App;
