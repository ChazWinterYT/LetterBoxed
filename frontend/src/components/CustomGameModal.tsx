import React from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import "./css/CustomSeedWordsForm.css";


interface CustomGameModalProps {
  onClose: () => void;
}

const CustomGameModal: React.FC<CustomGameModalProps> = ({ 
  onClose,
}) => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>
          X
        </button>
        <h1 className="modal-title">{t("game.customGame.customGameTitle")}</h1>
        <div className="modal-body">
          <h3>{t("game.customGame.customGameChoice")}</h3>
          <div className="button-group">
            <div className="button-option">
              <button
                className="modal-button"
                onClick={() => {
                  onClose(); // Close this modal
                  navigate("/create-game-seed-words") // Open the Seed Words page
                }}
              >
                {t("game.customGame.chooseWords")}
              </button>
              <p>{t("game.customGame.chooseWordsDesc")}</p>
            </div>
            <div className="button-option">
              <button
                className="modal-button"
                onClick={() => {
                  onClose(); // Close this modal
                  navigate("/create-game-enter-letters") // Open the Enter Letters game page
                }}
              >
                {t("game.customGame.enterLetters")}
              </button>
              <p>{t("game.customGame.enterLettersDesc")}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomGameModal;
