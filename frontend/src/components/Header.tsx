import React from 'react';
import './css/Header.css';

const Header = () => (
  <header className="header">
    <div className="logo">chazwinter.com</div>
    <h2>Stitch-uations - A LetterBoxed Game!</h2>
    <select className="language-selector">
      <option value="en">English</option>
      <option value="de">Deutsch</option>
      <option value="es">Español</option>
      <option value="fr">Français</option>
      <option value="it">Italiano</option>
      <option value="sv">Svenska</option>
      <option value="pl">Polski</option>
    </select>
  </header>
);

export default Header;