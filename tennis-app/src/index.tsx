import "./index.css";

import App from "pages/App/App";
import React from "react";
import {createRoot} from "react-dom/client";
import TagManager from "react-gtm-module";
import {QueryClientProvider} from "react-query";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";

import queryClient from "./data/queryClient";

declare global {
    interface Window {
        config: any;
    }
}

if (window.config.GTM_ID.startsWith("GTM-")) {
    TagManager.initialize({gtmId: window.config.GTM_ID});
}


// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
const root = createRoot(document.getElementById("tennis-app")!);
const appi = (
    <Router>
        <React.StrictMode>
            <QueryClientProvider client={queryClient}>
            <Routes>
                    <Route path="/app" element={<App />}>
                    </Route>
            </Routes>
            </QueryClientProvider>
        </React.StrictMode>
    </Router>
);
root.render(appi);

