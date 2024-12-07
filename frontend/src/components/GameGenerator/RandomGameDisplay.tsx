import React from "react";

interface RandomGameDisplayProps {
  gameType: "singleWord" | "wordPair";
  content: string | [string, string];
}

const RandomGameDisplay: React.FC<RandomGameDisplayProps> = ({ gameType, content }) => {
  return (
    <div className="random-game-display">
      {gameType === "singleWord" ? (
        <p>{content as string}</p>
      ) : (
        <p>
          {content[0]} <span> + </span> {content[1]}
        </p>
      )}
    </div>
  );
};

export default RandomGameDisplay;
