import React from 'react';

type ArchiveListProps = {
  games: string[]; 
};

const ArchiveList: React.FC<ArchiveListProps> = ({ games }) => {
  if (!games || games.length === 0) {
    return <p>No games available.</p>; // Graceful fallback
  }

  return (
    <ul>
      {games.map((game, index) => (
        <li key={index}>{game}</li> // Render each date
      ))}
    </ul>
  );
};

export default ArchiveList;