import React from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import "./css/ButtonMenu.css"; 

interface ButtonMenuProps {
  onPlayToday: () => void;
  onOpenArchive: () => void;
  onOpenCustomGame: () => void;
  onPlayRandomGame: () => void;
}

const ButtonMenu: React.FC<ButtonMenuProps> = ({
  onPlayToday,
  onOpenArchive,
  onOpenCustomGame,
  onPlayRandomGame,
}) => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  return (
    <div className="button-menu">
      <button
        onClick={() => {
          navigate("/"); // Reset the URL to "/"
          onPlayToday(); // Explicitly reload today's game
        }}
      >
        {t("ui.menu.playToday")}
      </button>
      <button onClick={onOpenArchive}>{t("ui.menu.archive")}</button>
      <button onClick={onOpenCustomGame}>{t("ui.menu.customGame")}</button>
      <button onClick={onPlayRandomGame}>{t("ui.menu.randomGame")}</button>
      <button 
        onClick={() => window.location.href = "/LetterBoxed/frontend/get-word-pairs"}
      >
        {t("ui.menu.getWordPairs")}
      </button>
    </div>
  );
};

export default ButtonMenu;
