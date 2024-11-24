import React from 'react';
import ReactDOM from 'react-dom';
import App from './App'; // Main App component

// Render the App into the #root div in public/index.html
ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
