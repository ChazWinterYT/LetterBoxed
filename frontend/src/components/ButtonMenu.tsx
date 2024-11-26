import React from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import "./css/ButtonMenu.css"; 

interface ButtonMenuProps {
  onPlayToday: () => void;
  onOpenArchive: () => void;
  onOpenCustomGame: () => void;
}

const ButtonMenu: React.FC<ButtonMenuProps> = ({
  onPlayToday,
  onOpenArchive,
  onOpenCustomGame,
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
    </div>
  );
};

export default ButtonMenu;
