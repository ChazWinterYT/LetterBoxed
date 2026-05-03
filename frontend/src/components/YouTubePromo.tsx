import React from "react";
import { useLanguage } from "../context/LanguageContext";
import "./css/YouTubePromo.css";

type PromoVideo = {
  title: string;
  description: string;
  url: string;
  thumbnailUrl: string;
};

const promoVideos: PromoVideo[] = [
  {
    title: "AIs Play Poker Episode 4",
    description: "Watch 9 real LLMs compete in a full poker tournament, complete with trash talk.",
    url: "https://www.youtube.com/@ChazWinter",
    thumbnailUrl: `${process.env.PUBLIC_URL}/Ep4Part1thumb-Eng.jpg`,
  },
  {
    title: "Chaz Winter on YouTube",
    description: "Watch 8 real LLMs choose Pokemon and battle tournament-style.",
    url: "https://www.youtube.com/@ChazWinter",
    thumbnailUrl: `${process.env.PUBLIC_URL}/Ep2Part1-thumbnail-Eng.jpg`,
  },
];

const YouTubePromo: React.FC = () => {
  const { t } = useLanguage();

  return (
    <section className="youtube-promo" aria-labelledby="youtube-promo-title">
      <h2 id="youtube-promo-title">{t("ui.youtubePromo.heading")}</h2>
      <div className="youtube-promo-list">
        {promoVideos.map((video) => (
          <a
            className="youtube-promo-video"
            href={video.url}
            key={video.title}
            rel="noopener noreferrer"
            target="_blank"
          >
            <div className="youtube-promo-thumbnail">
              <img src={video.thumbnailUrl} alt="" loading="lazy" />
              <span className="youtube-promo-play" aria-hidden="true" />
            </div>
            <div className="youtube-promo-copy">
              <h3>{video.title}</h3>
              <p>{video.description}</p>
              <span>{t("ui.youtubePromo.watchOnYouTube")}</span>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
};

export default YouTubePromo;
