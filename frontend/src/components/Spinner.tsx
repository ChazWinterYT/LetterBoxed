import React from "react";
import "./css/Spinner.css";

type SpinnerProps = {
  message?: string; // Optional message
};

const Spinner: React.FC<SpinnerProps> = ({ message }) => {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      {message && <p className="spinner-message">{message}</p>} {/* Display message */}
    </div>
  );
};

export default Spinner;
