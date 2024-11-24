import React from 'react';

interface ArchiveListProps {
  games: any[];
}

const ArchiveList: React.FC<ArchiveListProps> = ({ games }) => (
  <div>
    <h2>NYT Games Archive</h2>
    <ul>
      {games.map((game, index) => (
        <li key={index}>
          <a href={`/game/${game.uuid}`}>{game.date}</a>
        </li>
      ))}
    </ul>
  </div>
);

export default ArchiveList;
