import React from 'react';
import './css/Spinner.css';

interface SpinnerProps {
  message: string;
  isModal?: boolean; // New optional prop to indicate modal usage
}

const Spinner: React.FC<SpinnerProps> = ({ message, isModal = false }) => {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p className="spinner-message">{message}</p>
    </div>
  );
};

export default Spinner;
