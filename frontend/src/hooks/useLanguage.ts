/**
 * useLanguage Hook
 * Provides translation functionality based on user's language preference
 */
import { useState, useEffect, useCallback } from 'react';
import { translations, Language, TranslationKey } from '../i18n/translations';

export const useLanguage = (initialLanguage: Language = 'en') => {
  const [currentLanguage, setCurrentLanguage] = useState<Language>(initialLanguage);

  // Function to get translated text
  const t = useCallback((key: TranslationKey): string => {
    const lang = translations[currentLanguage] || translations.en;
    return lang[key] || translations.en[key] || key;
  }, [currentLanguage]);

  // Function to change language
  const changeLanguage = useCallback((newLanguage: Language) => {
    console.log('🌐 Changing UI language to:', newLanguage);
    setCurrentLanguage(newLanguage);
    // Store in localStorage for persistence
    localStorage.setItem('orbis_ui_language', newLanguage);
  }, []);

  // Load language from localStorage on mount
  useEffect(() => {
    const storedLanguage = localStorage.getItem('orbis_ui_language') as Language;
    if (storedLanguage && translations[storedLanguage]) {
      setCurrentLanguage(storedLanguage);
    }
  }, []);

  return {
    currentLanguage,
    changeLanguage,
    t
  };
};
