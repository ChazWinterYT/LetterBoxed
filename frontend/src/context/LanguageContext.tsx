import React, { createContext, useContext, useState, useEffect } from "react";
import languages, { Language } from "../languages/languages"; // Language metadata
import translations from "../languages/index"; // Translations JSON object

type Translations = {
  [languageCode: string]: {
    [key: string]: any; // Nested structure for translations
  };
};

const typedTranslations: Translations = translations as Translations;

interface LanguageContextProps {
  language: string; // Current UI language
  setLanguage: (lang: string) => void; // Function to set the language
  t: (key: string) => string; // Translate a given key
  getRandomPhrase: (key: string) => string; // Get a random phrase from translations
  availableLanguages: typeof languages;
  isPlayable: (code: string) => boolean; // Check if a language is playable
}

const LanguageContext = createContext<LanguageContextProps | undefined>(
  undefined
);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [language, setLanguage] = useState<string>(() => {
    // Load saved language from localStorage or fallback to "en"
    return localStorage.getItem("language") || "en";
  });

  useEffect(() => {
    // Save the selected language to localStorage whenever it changes
    localStorage.setItem("language", language);
  }, [language]);

  // Declare availableLanguages here
  const availableLanguages = languages; // Import from languages.ts

  const t = (key: string): string => {
    const keys = key.split(".");
    let translation: any = typedTranslations[language]; // Use the current language for translations

    for (const k of keys) {
      if (translation && typeof translation === "object") {
        translation = translation[k];
      } else {
        break; // Exit loop if translation is not an object
      }
    }

    return typeof translation === "string" ? translation : key; // Return the translation if it's a string, otherwise fallback to the key
  };

  const getRandomPhrase = (key: string): string => {
    const keys = key.split(".");
    let translation: any = typedTranslations[language];

    for (const k of keys) {
      if (translation && typeof translation === "object") {
        translation = translation[k];
      } else {
        break; // Exit loop if translation is not an object
      }
    }

    if (Array.isArray(translation)) {
      const randomIndex = Math.floor(Math.random() * translation.length);
      return translation[randomIndex];
    }

    console.warn(`Translation key "${key}" does not point to an array.`);
    return key; // Fallback to the key if it's not an array
  };

  const isPlayable = (code: string): boolean => {
    const lang = availableLanguages.find((lang) => lang.code === code && lang.playable);
    return !!lang;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        getRandomPhrase,
        availableLanguages,
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
