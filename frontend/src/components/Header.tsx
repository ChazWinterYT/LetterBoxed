import React from "react";
import { useLanguage } from "../context/LanguageContext";
import LanguageSelector from "./LanguageSelector";
import "./css/Header.css";

const Header = () => {
  const { t, language, setLanguage, availableLanguages } = useLanguage(); // Use uiLanguages from context

  return (
    <header className="header">
      <div className="logo">chazwinter.com</div>
      <h2>{t("header.title")}</h2>
      <h3>{t("header.subtitle")}</h3>
      <select
        className="language-selector"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
      >
        {availableLanguages
          .filter((lang) => lang.uiAvailable) // Ensure only UI-available languages appear
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
