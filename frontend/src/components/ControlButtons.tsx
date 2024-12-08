import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/ControlButtons.css'

interface ControlButtonsProps {
  onDelete: () => void;
  onRemoveLastWord: () => void;
  onRestart: () => void;
  onSubmit: () => void;
  onShowHint: () => void;
  onShuffle: () => void;
  gameCompleted: boolean;
}

const ControlButtons: React.FC<ControlButtonsProps> = ({
  onDelete,
  onRemoveLastWord,
  onRestart,
  onSubmit,
  onShowHint,
  onShuffle,
  gameCompleted,
}) => {
  const { t } = useLanguage();

  return (
    <div className="controls">
      <div className="control-row">
        <button className="delete-button" onClick={onDelete} disabled={gameCompleted}>
          {t('game.deleteLetter')}
        </button>
        <button className="remove-last-button" onClick={onRemoveLastWord} disabled={gameCompleted}>
          {t("game.removeLastWord")}
        </button>
        <button className="submit-button" onClick={onSubmit} disabled={gameCompleted}>
          {t('game.submitWord')}
        </button>
      </div>
      <div className="control-row">
        <button className="restart-button" onClick={onRestart}>
          {t('game.restartGame')}
        </button>
        <button className="shuffle-button" onClick={onShuffle} disabled={gameCompleted}>
          {t('game.shuffle')}
        </button> 
        <button className="hint-button" onClick={onShowHint}>
          {t('game.showHint')}
        </button>
      </div>
    </div>
  );
};

export default ControlButtons;
