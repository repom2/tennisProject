import React from 'react';
import ReactDOM from 'react-dom/client';
import "./index.css";
import App from './App';
import { QueryClientProvider } from 'react-query';
import queryClient from "./data/queryClient";

const rootElement = document.getElementById('root');

if (!rootElement) {
    throw new Error("Root element not found");
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
  <QueryClientProvider client={queryClient}>
    <App />
   </QueryClientProvider>
  </React.StrictMode>
);

if(module.hot){
    module.hot.accept()
}
