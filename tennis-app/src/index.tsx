import "./index.css";

import App from "pages/App/App";
import React from "react";
import {createRoot} from "react-dom/client";
import TagManager from "react-gtm-module";

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
const app = <App />;
root.render(app);
