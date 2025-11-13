/**
 * TranslationBar Component - Premium Design
 * Shows language settings and translation controls
 */
import React from 'react';
import { Languages, Subtitles, ArrowRight } from 'lucide-react';

interface TranslationBarProps {
  inputLanguage: string;
  outputLanguage: string;
  onLanguageClick: () => void;
  onToggleCaptions: () => void;
  showCaptions: boolean;
}

const LANGUAGE_NAMES: Record<string, string> = {
  'auto': 'Auto-detect',
  'en': 'English',
  'pt': 'Portuguese',
  'es': 'Spanish',
  'fr': 'French',
  'de': 'German',
  'it': 'Italian',
  'ja': 'Japanese',
  'ko': 'Korean',
  'zh': 'Chinese',
  'ar': 'Arabic',
  'ru': 'Russian',
  'hi': 'Hindi'
};

const TranslationBar: React.FC<TranslationBarProps> = ({
  inputLanguage,
  outputLanguage,
  onLanguageClick,
  onToggleCaptions,
  showCaptions
}) => {
  return (
    <div className="glass-dark border-t border-white/10 px-6 py-4 backdrop-blur-xl">
      <div className="flex items-center justify-between">
        {/* Language info */}
        <button
          onClick={onLanguageClick}
          className="flex items-center gap-3 glass hover:bg-white/10 px-5 py-3 rounded-xl transition-all hover:scale-105 group shadow-lg"
        >
          <div className="bg-gradient-to-br from-red-500 to-red-600 p-2 rounded-lg shadow-lg">
            <Languages size={20} className="text-white" />
          </div>
          <div className="text-left">
            <div className="text-white font-semibold flex items-center gap-2">
              {LANGUAGE_NAMES[inputLanguage] || inputLanguage}
              <ArrowRight size={16} className="text-red-400" />
              {LANGUAGE_NAMES[outputLanguage] || outputLanguage}
            </div>
            <div className="text-gray-400 text-xs group-hover:text-gray-300 transition-colors">
              Click to change languages
            </div>
          </div>
        </button>
        
        {/* Caption toggle */}
        <button
          onClick={onToggleCaptions}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl transition-all hover:scale-105 shadow-lg ${
            showCaptions 
              ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white shadow-[0_0_40px_rgba(220,38,38,0.3)]' 
              : 'glass hover:bg-white/10 text-gray-300'
          }`}
        >
          <Subtitles size={20} />
          <span className="font-semibold">
            {showCaptions ? 'Hide' : 'Show'} Captions
          </span>
        </button>
      </div>
    </div>
  );
};

export default TranslationBar;