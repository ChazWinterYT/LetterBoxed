import React from 'react';
import './css/LeftMenu.css';

interface LeftMenuProps {
  onOptionSelect: (option: string) => void;
}

const LeftMenu: React.FC<LeftMenuProps> = ({ onOptionSelect }) => (
  <aside className="left-menu">
    <h2>Menu</h2>
    <ul>
      <li onClick={() => onOptionSelect('play-today')}>Play Today’s NYT Game</li>
      <li onClick={() => onOptionSelect('archive')}>NYT Games Archive</li>
      <li onClick={() => onOptionSelect('custom-game')}>Create Custom Game</li>
      <li onClick={() => onOptionSelect('random-game')}>Create Random Game</li>
    </ul>
  </aside>
);

export default LeftMenu;
