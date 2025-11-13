/**
 * Language Context
 * Global language state management for the entire app
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translations, Language, TranslationKey } from '../i18n/translations';

interface LanguageContextType {
  currentLanguage: Language;
  changeLanguage: (newLanguage: Language) => void;
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
  initialLanguage?: Language;
}

// Helper function to detect initial language
const detectInitialLanguage = (): Language => {
  // Check localStorage first (user preference)
  const storedLanguage = localStorage.getItem('orbis_ui_language') as Language;
  if (storedLanguage && translations[storedLanguage]) {
    console.log('🌐 Loaded language from localStorage:', storedLanguage);
    return storedLanguage;
  }

  // Auto-detect from browser
  const browserLang = navigator.language || (navigator as any).userLanguage || 'en';
  console.log('🌍 Browser language detected:', browserLang);
  
  // Extract language code (e.g., 'pt-BR' -> 'pt', 'en-US' -> 'en')
  const langCode = browserLang.split('-')[0].toLowerCase();
  
  // Check if we support this language
  const supportedLanguages: Language[] = ['en', 'pt', 'fr', 'es', 'de'];
  const detectedLanguage = supportedLanguages.includes(langCode as Language) 
    ? (langCode as Language) 
    : 'en';
  
  console.log('✅ Auto-detected language:', detectedLanguage);
  
  // Save to localStorage
  localStorage.setItem('orbis_ui_language', detectedLanguage);
  
  return detectedLanguage;
};

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children, initialLanguage }) => {
  // Use detected language if no initialLanguage provided
  const [currentLanguage, setCurrentLanguage] = useState<Language>(
    initialLanguage || detectInitialLanguage()
  );

  // Function to get translated text
  const t = (key: TranslationKey): string => {
    const lang = translations[currentLanguage] || translations.en;
    return lang[key] || translations.en[key] || key;
  };

  // Function to change language
  const changeLanguage = (newLanguage: Language) => {
    console.log('🌐 Changing global UI language to:', newLanguage);
    setCurrentLanguage(newLanguage);
    // Store in localStorage for persistence
    localStorage.setItem('orbis_ui_language', newLanguage);
  };

  return (
    <LanguageContext.Provider value={{ currentLanguage, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook to use language context
export const useLanguageContext = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguageContext must be used within a LanguageProvider');
  }
  return context;
};
