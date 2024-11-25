import languages, { Language } from "../languages";

const PlayableLanguageSelector = () => (
  <select>
    {languages
      .filter((lang) => lang.playable)
      .map((lang: Language) => (
        <option key={lang.code} value={lang.code}>
          {lang.name}
        </option>
      ))}
  </select>
);
