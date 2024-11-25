export interface Language {
  code: string;
  name: string;
  uiAvailable: boolean;
  playable: boolean;
}

const languages: Language[] = [
  { code: "en", name: "English", uiAvailable: true, playable: true },
  { code: "de", name: "Deutsch", uiAvailable: true, playable: false },
  { code: "es", name: "Español", uiAvailable: true, playable: false },
  { code: "fr", name: "Français", uiAvailable: true, playable: false },
  { code: "hi", name: "हिंदी", uiAvailable: true, playable: false },
  { code: "id", name: "Bahasa Indonesia", uiAvailable: true, playable: false },
  { code: "it", name: "Italiano", uiAvailable: true, playable: false },
  { code: "ja", name: "日本語", uiAvailable: true, playable: false },
  { code: "pl", name: "Polski", uiAvailable: true, playable: false },
  { code: "pt", name: "Português", uiAvailable: true, playable: false },
  { code: "ru", name: "Русский", uiAvailable: true, playable: false },
  { code: "sv", name: "Svenska", uiAvailable: true, playable: false },
];

export default languages;
