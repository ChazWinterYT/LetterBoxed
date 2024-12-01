import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/ControlButtons.css'

interface ControlButtonsProps {
  onDelete: () => void;
  onRestart: () => void;
  onSubmit: () => void;
  onShowHint: () => void;
  gameCompleted: boolean;
}

const ControlButtons: React.FC<ControlButtonsProps> = ({
  onDelete,
  onRestart,
  onSubmit,
  onShowHint,
  gameCompleted,
}) => {
  const { t } = useLanguage();

  return (
    <div className="controls">
      <div className="control-row">
          <button onClick={onDelete} disabled={gameCompleted}>
          {t('game.deleteLetter')}
          </button>
          <button onClick={onSubmit} disabled={gameCompleted}>
          {t('game.submitWord')}
          </button>
      </div>
      <div className="control-row">
          <button onClick={onRestart}>
          {t('game.restartGame')}
          </button>
          <button onClick={onShowHint}>
          {t('game.showHint')}
          </button>
      </div>
    </div>
  );
};

export default ControlButtons;
