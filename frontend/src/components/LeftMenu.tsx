import React from 'react';
import './css/LeftMenu.css';

interface LeftMenuProps {
  onOptionSelect: (option: string) => void;
}

const LeftMenu: React.FC<LeftMenuProps> = ({ onOptionSelect }) => (
  <aside className="left-menu">
    <h2>Menu</h2>
    <ul>
      <li onClick={() => onOptionSelect('random')}>Random Game</li>
      <li onClick={() => onOptionSelect('custom')}>Custom Game</li>
      <li onClick={() => onOptionSelect('basic')}>Basic Dictionary</li>
      <li onClick={() => onOptionSelect('full')}>Full Dictionary</li>
    </ul>
  </aside>
);

export default LeftMenu;
