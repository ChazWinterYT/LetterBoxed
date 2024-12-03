import { useLanguage } from "../context/LanguageContext";
import { Language } from "../languages/languages";

interface LanguageSelectorProps {
  filterKey?: "uiAvailable" | "playable"; // Filter for UI or playable languages
}

const LanguageSelector = ({ filterKey }: LanguageSelectorProps): Language[] => {
  const { availableLanguages } = useLanguage();

  return filterKey
    ? availableLanguages.filter((lang: Language) => lang[filterKey])
    : availableLanguages;
};

export default LanguageSelector;
