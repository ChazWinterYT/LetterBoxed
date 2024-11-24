import en from '../languages/en.json';
import es from '../languages/es.json';
import fr from '../languages/fr.json';
import de from '../languages/de.json';
import it from '../languages/it.json';
import pl from '../languages/pl.json';
import sv from '../languages/sv.json';

const languages: Record<string, any> = { en, es, fr, de, it, pl, sv };

export const getTranslation = (lang: string, key: string): string => {
  const langFile = languages[lang] || languages['en'];
  const keys = key.split('.');
  return keys.reduce((obj, k) => (obj && obj[k] ? obj[k] : null), langFile) || key;
};