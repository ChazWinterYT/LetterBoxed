import React, { useState } from "react";
import { useLanguage } from '../context/LanguageContext';
import { rateGame } from "../services/api";
import "./css/StarRating.css";

export interface StarRatingProps {
  gameId: string;
  maxStars?: number;
  averageRating?: number;
  onRatingSelect?: (rating: number) => void;
}

const StarRating: React.FC<StarRatingProps> = ({
  gameId,
  maxStars = 5,
  averageRating = 0.0,
  onRatingSelect,
}) => {
  const { t } = useLanguage();
  // Track which star is currently hovered (for highlighting)
  const [hoveredRating, setHoveredRating] = useState<number>(0);

  // Track which star rating is selected after clicking
  const [selectedRating, setSelectedRating] = useState<number>(0);

  // Update the average rating after a user adds a new rating
  const [localAverage, setLocalAverage] = useState<number>(averageRating);

  const handleClickStar = async (starValue: number) => {
    // Visually lock in the rating
    setSelectedRating(starValue);
    onRatingSelect?.(starValue);

    // Make the API call to rate the game
    try {
      const { totalStars, totalRatings } = await rateGame({
        gameId: gameId,
        stars: starValue,
      });

      if (totalStars !== undefined && totalRatings !== undefined && totalRatings > 0) {
        const newAverage = totalStars / totalRatings;
        setLocalAverage(newAverage);
      }

    } catch (error) {
      console.error("Error rating game:", error);
    }
  };

  return (
      <div className="star-rating-container">
        {/* Display Average Rating text */}
        <p className="average-rating-text">
          <b>{t("game.complete.averageRating")}:</b>{" "}
          {localAverage.toFixed(1)} / {maxStars}
        </p>

        {/* "Rate This Game" text */}
        <div className="rate-this-game-label">
          <p>{t("game.complete.rateThisGame")}:</p>
        </div>
        
        {/* Stars */}
        <div
          className="star-rating"
          onMouseLeave={() => setHoveredRating(0)}  // Reset hover when leaving container
        >
          {[...Array(maxStars)].map((_, i) => {
              const starValue = i + 1; // 1-based index

              // Determine the CSS class for styling
              let starClass = "star";
              if (hoveredRating >= starValue) {
              starClass += " hovered";
              } else if (selectedRating >= starValue) {
              starClass += " selected";
              }

              return (
              <span
                  key={starValue}
                  className={starClass}
                  onMouseEnter={() => setHoveredRating(starValue)} // Hover star
                  onClick={() => handleClickStar(starValue)}
              >
                  ★
              </span>
              );
          })}
        </div>
      </div>
  );
};

export default StarRating;
