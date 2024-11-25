import React from 'react';
import { useLanguage } from "../context/LanguageContext";

type ArchiveListProps = {
  games: string[]; 
};

const ArchiveList: React.FC<ArchiveListProps> = ({ games }) => {
  const { t } = useLanguage(); // Access the translation function
  
  if (!games || games.length === 0) {
    return <p>{t("ui.archive.noGames")}</p>;// Graceful fallback
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