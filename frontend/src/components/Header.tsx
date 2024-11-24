import React from 'react';
import './css/Header.css';

const Header = () => (
  <header className="header">
    <div className="logo">chazwinter.com</div>
    <h1>LetterBoxed Game</h1>
    <select className="language-selector">
      <option value="en">English</option>
      <option value="es">Español</option>
      <option value="fr">Français</option>
    </select>
  </header>
);

export default Header;