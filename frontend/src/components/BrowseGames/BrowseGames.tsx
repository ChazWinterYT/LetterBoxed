import React from "react";
import { useLanguage } from "../../context/LanguageContext";
import Header from "../Header";
import Footer from "../Footer";

const BrowseGames: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div>
      <Header />
      <button 
        className="menu-button"
        onClick={() => window.location.href = "/LetterBoxed/frontend"}
      >
        {t("ui.menu.returnHome")}
      </button>
      <div>
        Hi. This component isn't ready yet.
      </div>
      <Footer />
    </div>
  )
};

export default BrowseGames;