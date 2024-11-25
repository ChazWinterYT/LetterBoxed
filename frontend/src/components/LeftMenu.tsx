import React from 'react';
import './css/LeftMenu.css';
import { useLanguage } from '../context/LanguageContext'; // Import useLanguage hook

interface LeftMenuProps {
  onOptionSelect: (option: string) => void;
}

const LeftMenu: React.FC<LeftMenuProps> = ({ onOptionSelect }) => {
  const { t } = useLanguage(); // Get translation function from the hook

  return (
    <aside className="left-menu">
      <h2>{t('ui.menu.menuTitle')}</h2> {/* Add "menuTitle" to the language files */}
      <ul>
        <li onClick={() => onOptionSelect('play-today')}>{t('ui.menu.playToday')}</li>
        <li onClick={() => onOptionSelect('archive')}>{t('ui.menu.archive')}</li>
        <li onClick={() => onOptionSelect('custom-game')}>{t('ui.menu.customGame')}</li>
        <li onClick={() => onOptionSelect('random-game')}>{t('ui.menu.randomGame')}</li>
      </ul>
    </aside>
  );
};

export default LeftMenu;
