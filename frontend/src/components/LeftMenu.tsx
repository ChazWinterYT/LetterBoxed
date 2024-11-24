import React from 'react';
import './css/LeftMenu.css';

const LeftMenu = ({ onOptionSelect }: { onOptionSelect: (option: string) => void }) => (
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