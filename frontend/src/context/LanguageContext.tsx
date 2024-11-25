import React, { createContext, useContext, useState } from "react";
import translations from "../languages/index"; // Translations JSON object
import languages from "../languages"; // Language metadata

type Translations = {
  [languageCode: string]: {
    [key: string]: any; // Nested structure for translations
  };
};

const typedTranslations: Translations = translations as Translations;

interface LanguageContextProps {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
  availableLanguages: typeof languages;
  isPlayable: (code: string) => boolean;
}

const LanguageContext = createContext<LanguageContextProps | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<string>("en"); // Default language

  const t = (key: string): string => {
    const keys = key.split(".");
    let translation: any = typedTranslations[language]; // Start with the root translation for the current language

    for (const k of keys) {
      if (translation && typeof translation === "object") {
        translation = translation[k];
      } else {
        break; // Exit loop if translation is not an object
      }
    }

    return typeof translation === "string" ? translation : key; // Return the translation if it's a string, otherwise fallback to the key
  };

  const isPlayable = (code: string): boolean => {
    const lang = languages.find((lang) => lang.code === code);
    return lang?.playable || false;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        availableLanguages: languages,
        isPlayable,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};