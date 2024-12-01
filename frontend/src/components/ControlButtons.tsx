import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/ControlButtons.css'

interface ControlButtonsProps {
  onDelete: () => void;
  onRestart: () => void;
  onSubmit: () => void;
  gameCompleted: boolean;
}

const ControlButtons: React.FC<ControlButtonsProps> = ({
  onDelete,
  onRestart,
  onSubmit,
  gameCompleted,
}) => {
  const { t } = useLanguage();

  return (
    <div className="controls">
      <button onClick={onDelete} disabled={gameCompleted}>
        {t('game.deleteLetter')}
      </button>
      <button onClick={onRestart}>
        {t('game.restartGame')}
      </button>
      <button onClick={onSubmit} disabled={gameCompleted}>
        {t('game.submitWord')}
      </button>
    </div>
  );
};

export default ControlButtons;
