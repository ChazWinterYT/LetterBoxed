import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

interface CustomSeedWordsFormProps {
  onSubmit: (data: { boardSize: string; language: string; seedWords: string[] }) => void;
  onClose: () => void;
}

const CustomSeedWordsForm: React.FC<CustomSeedWordsFormProps> = ({ onSubmit, onClose }) => {
  const { t } = useLanguage(); // Access the `t` function for translations
  const [boardSize, setBoardSize] = useState('3x3');
  const [language, setLanguage] = useState('en');
  const [seedWords, setSeedWords] = useState<string[]>(['']);

  const handleAddSeedWord = () => {
    setSeedWords([...seedWords, '']);
  };

  const handleSeedWordChange = (index: number, value: string) => {
    const updatedSeedWords = [...seedWords];
    updatedSeedWords[index] = value;
    setSeedWords(updatedSeedWords);
  };

  const handleRemoveSeedWord = (index: number) => {
    const updatedSeedWords = seedWords.filter((_, i) => i !== index);
    setSeedWords(updatedSeedWords);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ boardSize, language, seedWords });
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        {t('form.boardSize')}
        <select value={boardSize} onChange={(e) => setBoardSize(e.target.value)}>
          <option value="2x2">{t('form.boardSizes.2x2')}</option>
          <option value="3x3">{t('form.boardSizes.3x3')}</option>
          <option value="4x4">{t('form.boardSizes.4x4')}</option>
        </select>
      </label>

      <label>
        {t('form.language')}
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">{t('languages.english')}</option>
          <option value="es">{t('languages.spanish')}</option>
          <option value="fr">{t('languages.french')}</option>
          {/* Add more language options as needed */}
        </select>
      </label>

      <div>
        {t('form.seedWords')}
        {seedWords.map((word, index) => (
          <div key={index}>
            <input
              type="text"
              value={word}
              onChange={(e) => handleSeedWordChange(index, e.target.value)}
              placeholder={t('form.placeholder.seedWord')}
            />
            <button type="button" onClick={() => handleRemoveSeedWord(index)}>
              {t('form.remove')}
            </button>
          </div>
        ))}
        <button type="button" onClick={handleAddSeedWord}>
          {t('form.addSeedWord')}
        </button>
      </div>

      <button type="submit">{t('form.generateGame')}</button>
      <button type="button" onClick={onClose}>
        {t('form.cancel')}
      </button>
    </form>
  );
};

export default CustomSeedWordsForm;
