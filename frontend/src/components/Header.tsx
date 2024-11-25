import React from "react";
import languages, { Language } from "../languages";
import "./css/Header.css";

const Header = () => (
  <header className="header">
    <div className="logo">chazwinter.com</div>
    <h2>Stitch-uations - A LetterBoxed Game!</h2>
    <select className="language-selector">
      {languages
        .filter((lang: Language) => lang.uiAvailable)
        .map((lang: Language) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
    </select>
  </header>
);

export default Header;
