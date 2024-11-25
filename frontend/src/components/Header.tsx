import React from "react";
import { useLanguage } from "../context/LanguageContext";
import "./css/Header.css";

const Header = () => {
  const { t, language, setLanguage, availableLanguages } = useLanguage();

  return (
    <header className="header">
      <div className="logo">chazwinter.com</div>
      <h2>{t("header.title")}</h2>
      <select
        className="language-selector"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
      >
        {availableLanguages
          .filter((lang) => lang.uiAvailable) // Only show UI-available languages
          .map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
      </select>
    </header>
  );
};

export default Header;
