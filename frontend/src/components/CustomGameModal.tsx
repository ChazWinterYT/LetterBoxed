import React from "react";
import { useLanguage } from "../context/LanguageContext";

interface CustomGameModalProps {
  onClose: () => void;
  onEnterLetters: () => void;
  onChooseWords: () => void;
}

const CustomGameModal: React.FC<CustomGameModalProps> = ({
  onClose,
  onEnterLetters,
  onChooseWords,
}) => {
  const { t } = useLanguage();

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
              <button className="modal-button" onClick={onChooseWords}>
                {t("game.customGame.chooseWords")}
              </button>
              <p>{t("game.customGame.chooseWordsDesc")}</p>
            </div>
            <div className="button-option">
              <button className="modal-button" onClick={onEnterLetters}>
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
