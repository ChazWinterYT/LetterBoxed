import React from 'react';
import { createRoot } from 'react-dom/client'; // Import createRoot
import App from './App';
import { LanguageProvider } from './context/LanguageContext';
import './index.css';

console.log('React index.tsx: Starting to mount app');
const container = document.getElementById('root');
if (!container) {
  console.error('React index.tsx: root container not found!');
} else {
  console.log('React index.tsx: root container found, creating root');
  const root = createRoot(container);
  console.log('React index.tsx: rendering app');
  root.render(
    <LanguageProvider>
      <App />
    </LanguageProvider>
  );
  console.log('React index.tsx: render called');
}