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
        className="menu-button play-today"
        onClick={() => {
          navigate("/"); // Reset the URL to "/"
          onPlayToday(); // Explicitly reload today's game
        }}
      >
        {t("ui.menu.playToday")}
      </button>
      <button className="menu-button archive" onClick={onOpenArchive}>
        {t("ui.menu.archive")}
      </button>
      <button
        className="menu-button browse-games"
        onClick={() => (window.location.href = "/LetterBoxed/frontend/browse-games")}
      >
        {t("ui.menu.browseGames")}
      </button>
      <button className="menu-button random-game" onClick={onPlayRandomGame}>
        {t("ui.menu.randomGame")}
      </button>
      <button className="menu-button custom-game" onClick={onOpenCustomGame}>
        {t("ui.menu.customGame")}
      </button>
      <button
        className="menu-button random-game-generator"
        onClick={() => (window.location.href = "/LetterBoxed/frontend/get-word-pairs")}
      >
        {t("ui.menu.randomGameGenerator")}
      </button>
    </div>
  );
};

export default ButtonMenu;
