import React, { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import CustomSeedWordsForm from "./CustomSeedWordsForm";
import "./css/CustomSeedWordsForm.css";

interface CustomGameModalProps {
  onClose: () => void;
  onOpenSeedWordsForm: () => void;
  onOpenEnterLettersForm: () => void;
}

const CustomGameModal: React.FC<CustomGameModalProps> = ({ 
  onClose,
  onOpenSeedWordsForm,
  onOpenEnterLettersForm,
}) => {
  const { t } = useLanguage();
  const [currentView, setCurrentView] = useState<"main" | "seedWords">("main");

  const handleBackToMain = () => {
    setCurrentView("main");
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>
          X
        </button>
        {currentView === "main" ? (
          <>
            <h1 className="modal-title">{t("game.customGame.customGameTitle")}</h1>
            <div className="modal-body">
              <h3>{t("game.customGame.customGameChoice")}</h3>
              <div className="button-group">
                <div className="button-option">
                  <button
                    className="modal-button"
                    onClick={() => {
                      onClose(); // Close this modal
                      onOpenSeedWordsForm(); // Open the Seed Words form modal
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
                      onOpenEnterLettersForm(); // Open the Enter Letters form modal
                    }}
                  >
                    {t("game.customGame.enterLetters")}
                  </button>
                  <p>{t("game.customGame.enterLettersDesc")}</p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <CustomSeedWordsForm
            onGenerate={(data) => {
              console.log("Generated Custom Game with:", data);
              onClose(); // Close the modal after game generation
            }}
            onCancel={handleBackToMain}
          />
        )}
      </div>
    </div>
  );
};

export default CustomGameModal;
