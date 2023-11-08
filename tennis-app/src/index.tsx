import "./index.css";

import App from "pages/App/App";
import React from "react";
import {createRoot} from "react-dom/client";
import TagManager from "react-gtm-module";
import {QueryClientProvider} from "react-query";
//import {ReactQueryDevtools} from "react-query/devtools";
import {BrowserRouter, Route, Routes} from "react-router-dom";

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
const app = (
    <BrowserRouter>
        <React.StrictMode>
            <QueryClientProvider client={queryClient}>
                    <Routes>
                        <Route path="/*" element={<App />} />
                    </Routes>
                {/*<ReactQueryDevtools position={"top-right"} />*/}
            </QueryClientProvider>
        </React.StrictMode>
    </BrowserRouter>
);
root.render(app);

