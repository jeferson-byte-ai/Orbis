/**
 * LanguageSelector Component - Premium Design
 * Modal for selecting input and output languages
 */
import React, { useState } from 'react';
import { X, Check, Search } from 'lucide-react';

interface LanguageSelectorProps {
  currentInput: string;
  currentOutput: string;
  onSave: (input: string, output: string) => void;
  onClose: () => void;
}

const LANGUAGES = [
  { code: 'auto', name: 'Auto-detect', flag: '🌍' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'pt', name: 'Portuguese', flag: '🇧🇷' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'de', name: 'German', flag: '🇩🇪' },
  { code: 'it', name: 'Italian', flag: '🇮🇹' },
  { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', flag: '🇰🇷' },
  { code: 'zh', name: 'Chinese (Simplified)', flag: '🇨🇳' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
  { code: 'ru', name: 'Russian', flag: '🇷🇺' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'nl', name: 'Dutch', flag: '🇳🇱' },
  { code: 'pl', name: 'Polish', flag: '🇵🇱' },
  { code: 'tr', name: 'Turkish', flag: '🇹🇷' },
  { code: 'sv', name: 'Swedish', flag: '🇸🇪' },
  { code: 'no', name: 'Norwegian', flag: '🇳🇴' },
  { code: 'da', name: 'Danish', flag: '🇩🇰' },
  { code: 'fi', name: 'Finnish', flag: '🇫🇮' },
  { code: 'cs', name: 'Czech', flag: '🇨🇿' },
  { code: 'el', name: 'Greek', flag: '🇬🇷' },
  { code: 'he', name: 'Hebrew', flag: '🇮🇱' },
  { code: 'id', name: 'Indonesian', flag: '🇮🇩' },
  { code: 'th', name: 'Thai', flag: '🇹🇭' },
  { code: 'vi', name: 'Vietnamese', flag: '🇻🇳' }
];

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  currentInput,
  currentOutput,
  onSave,
  onClose
}) => {
  const [selectedInput, setSelectedInput] = useState(currentInput);
  const [selectedOutput, setSelectedOutput] = useState(currentOutput);
  const [searchInput, setSearchInput] = useState('');
  const [searchOutput, setSearchOutput] = useState('');
  
  const handleSave = () => {
    onSave(selectedInput, selectedOutput);
  };
  
  const filteredInputLanguages = LANGUAGES.filter(lang => 
    lang.name.toLowerCase().includes(searchInput.toLowerCase())
  );
  
  const filteredOutputLanguages = LANGUAGES.filter(lang => 
    lang.code !== 'auto' && lang.name.toLowerCase().includes(searchOutput.toLowerCase())
  );

  return (
    <div className="glass-dark rounded-3xl max-w-5xl w-full max-h-[90vh] overflow-hidden shadow-2xl border border-white/20 animate-scale-in">
        {/* Header */}
        <div className="glass px-6 py-5 flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-500 p-2 rounded-xl">
              <Languages size={24} className="text-white" />
            </div>
            <h2 className="text-white text-2xl font-bold">Select Languages</h2>
          </div>
          <button
            onClick={onClose}
            className="glass hover:bg-white/10 p-2 rounded-xl transition-all hover:rotate-90"
          >
            <X size={24} className="text-white" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Input Language */}
            <div>
              <h3 className="text-white text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-blue-500 text-white text-sm px-2 py-1 rounded">FROM</span>
                I speak
              </h3>
              
              {/* Search */}
              <div className="relative mb-4">
                <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search languages..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full glass text-white pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
                />
              </div>
              
              <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                {filteredInputLanguages.map((lang) => (
                  <LanguageOption
                    key={`input-${lang.code}`}
                    language={lang}
                    isSelected={selectedInput === lang.code}
                    onClick={() => setSelectedInput(lang.code)}
                  />
                ))}
              </div>
            </div>
            
            {/* Output Language */}
            <div>
              <h3 className="text-white text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-purple-500 text-white text-sm px-2 py-1 rounded">TO</span>
                Translate to
              </h3>
              
              {/* Search */}
              <div className="relative mb-4">
                <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search languages..."
                  value={searchOutput}
                  onChange={(e) => setSearchOutput(e.target.value)}
                  className="w-full glass text-white pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-400"
                />
              </div>
              
              <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                {filteredOutputLanguages.map((lang) => (
                  <LanguageOption
                    key={`output-${lang.code}`}
                    language={lang}
                    isSelected={selectedOutput === lang.code}
                    onClick={() => setSelectedOutput(lang.code)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <div className="glass px-6 py-5 flex items-center justify-end gap-3 border-t border-white/10">
          <button
            onClick={onClose}
            className="glass hover:bg-white/10 text-white px-8 py-3 rounded-xl transition-all font-semibold"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-xl transition-all flex items-center gap-2 font-bold shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
          >
            <Check size={20} />
            Save Changes
          </button>
        </div>
    </div>
  );
};

interface LanguagesType {
  code: string;
  name: string;
  flag: string;
}

const Languages = ({ size, className }: { size: number; className?: string }) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m5 8 6 6" />
      <path d="m4 14 6-6 2-3" />
      <path d="M2 5h12" />
      <path d="M7 2h1" />
      <path d="m22 22-5-10-5 10" />
      <path d="M14 18h6" />
    </svg>
  );
};

interface LanguageOptionProps {
  language: { code: string; name: string; flag: string };
  isSelected: boolean;
  onClick: () => void;
}

const LanguageOption: React.FC<LanguageOptionProps> = ({
  language,
  isSelected,
  onClick
}) => {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all hover:scale-105 ${
        isSelected
          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
          : 'glass hover:bg-white/10 text-gray-300'
      }`}
    >
      <span className="text-2xl">{language.flag}</span>
      <span className="flex-1 text-left font-semibold">{language.name}</span>
      {isSelected && (
        <div className="bg-white/20 p-1 rounded-full">
          <Check size={18} />
        </div>
      )}
    </button>
  );
};

export default LanguageSelector;