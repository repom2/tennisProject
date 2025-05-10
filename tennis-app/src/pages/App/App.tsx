import "./App.css";

import React from "react";
import {QueryClientProvider} from "react-query";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";

import {FootballTips} from "/app/src/components/FootballTips/FootballTips";
import {PlayerList} from "/app/src/components/Player/PlayerList";
import {Tips} from "/app/src/components/Tips/Tips";
import MatchProbabilityForm from "/app/src/components/MatchProbability/MatchProbabilityForm";
import queryClient from "/app/src/data/queryClient";

import {Header} from "./Header/Header";
import Sidebar from "./Sidebar/Sidebar";

function App() {
    return (
        <>
            <Router>
                <React.StrictMode>
                    <QueryClientProvider client={queryClient}>
                        <div className="App" />
                        <Header />
                        <div className="appContainer">
                            <Sidebar />
                            <Routes>
                                <Route path="/elo" element={<PlayerList />} />
                                <Route path="/tips-wta" element={<Tips level="wta" />} />
                                <Route path="/tips-atp" element={<Tips level="atp" />} />
                                <Route path="/footballtips" element={<FootballTips />} />
                                <Route path="/match-probability" element={<MatchProbabilityForm />} />
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
