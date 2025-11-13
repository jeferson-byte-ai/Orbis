/**
 * Language Configuration Modal
 * Allows users to configure languages they speak and understand during meetings
 */
import React, { useState, useEffect } from 'react';
import { X, Check, Globe, Mic, Ear, Search, Loader } from 'lucide-react';

interface Language {
  code: string;
  name: string;
  native_name: string;
  flag: string;
}

interface LanguageConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentSpeaksLanguages: string[];
  currentUnderstandsLanguages: string[];
  onSave: (speaks: string[], understands: string[]) => Promise<void>;
}

const LanguageConfigModal: React.FC<LanguageConfigModalProps> = ({
  isOpen,
  onClose,
  currentSpeaksLanguages,
  currentUnderstandsLanguages,
  onSave
}) => {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [speaksLanguages, setSpeaksLanguages] = useState<string[]>(currentSpeaksLanguages);
  const [understandsLanguages, setUnderstandsLanguages] = useState<string[]>(currentUnderstandsLanguages);

  useEffect(() => {
    if (isOpen) {
      loadLanguages();
      setSpeaksLanguages(currentSpeaksLanguages);
      setUnderstandsLanguages(currentUnderstandsLanguages);
    }
  }, [isOpen, currentSpeaksLanguages, currentUnderstandsLanguages]);

  const loadLanguages = async () => {
    setLoading(true);
    try {
      // Endpoint público - não precisa de autenticação
      const response = await fetch('http://localhost:8000/api/profile/languages/supported');

      if (!response.ok) {
        throw new Error(`Failed to load languages: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Languages loaded:', data.total, 'languages');
      
      if (data.languages && data.languages.length > 0) {
        setLanguages(data.languages);
      } else {
        console.error('❌ No languages returned from API');
      }
    } catch (error) {
      console.error('❌ Error loading languages:', error);
      // Fallback com idiomas básicos
      setLanguages([
        { code: 'en', name: 'English', native_name: 'English', flag: '🇬🇧' },
        { code: 'pt', name: 'Portuguese', native_name: 'Português', flag: '🇧🇷' },
        { code: 'es', name: 'Spanish', native_name: 'Español', flag: '🇪🇸' },
        { code: 'fr', name: 'French', native_name: 'Français', flag: '🇫🇷' },
        { code: 'de', name: 'German', native_name: 'Deutsch', flag: '🇩🇪' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSpeaks = (code: string) => {
    setSpeaksLanguages(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : [...prev, code]
    );
  };

  const toggleUnderstands = (code: string) => {
    setUnderstandsLanguages(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : [...prev, code]
    );
  };

  const handleSave = async () => {
    if (speaksLanguages.length === 0) {
      alert('Please select at least one language you speak');
      return;
    }
    if (understandsLanguages.length === 0) {
      alert('Please select at least one language you understand');
      return;
    }

    setSaving(true);
    try {
      await onSave(speaksLanguages, understandsLanguages);
      onClose();
    } catch (error) {
      console.error('Error saving languages:', error);
      alert('Failed to save language settings');
    } finally {
      setSaving(false);
    }
  };

  const filteredLanguages = languages.filter(lang =>
    lang.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lang.native_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lang.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-gradient-to-br from-gray-900 to-black border border-red-500/30 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600/20 to-purple-600/20 p-6 border-b border-red-500/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-purple-600 flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Language Settings</h2>
                <p className="text-sm text-gray-400">Configure languages for real-time translation</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-8 h-8 text-red-500 animate-spin" />
              <span className="ml-3 text-gray-400">Loading languages...</span>
            </div>
          ) : (
            <>
              {/* Search */}
              <div className="mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search languages..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition-colors"
                  />
                </div>
              </div>

              {/* Instructions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-gradient-to-br from-green-600/10 to-green-800/10 border border-green-500/30 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Ear className="w-5 h-5 text-green-400" />
                    <h3 className="text-lg font-semibold text-white">I Want to Hear In</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Language you want to HEAR in this meeting. Other participants will be translated to this language.
                  </p>
                  <div className="mt-2 text-sm text-green-400">
                    Selected: {understandsLanguages.length} language{understandsLanguages.length !== 1 ? 's' : ''}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-blue-600/10 to-blue-800/10 border border-blue-500/30 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Mic className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">I Will Speak In</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Language you will SPEAK. Your voice will be translated so others understand you.
                  </p>
                  <div className="mt-2 text-sm text-blue-400">
                    Selected: {speaksLanguages.length} language{speaksLanguages.length !== 1 ? 's' : ''}
                  </div>
                </div>
              </div>

              {/* Language Grid */}
              <div className="space-y-2">
                {filteredLanguages.map((lang) => (
                  <div
                    key={lang.code}
                    className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{lang.flag}</span>
                        <div>
                          <div className="text-white font-medium">{lang.name}</div>
                          <div className="text-sm text-gray-400">{lang.native_name}</div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        {/* Understands checkbox (PRIMEIRO - o que eu quero entender) */}
                        <button
                          onClick={() => toggleUnderstands(lang.code)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                            understandsLanguages.includes(lang.code)
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                          }`}
                          title="Quero entender neste idioma"
                        >
                          <Ear className="w-4 h-4" />
                          {understandsLanguages.includes(lang.code) && <Check className="w-4 h-4" />}
                        </button>

                        {/* Speaks checkbox (SEGUNDO - idioma que eu vou falar) */}
                        <button
                          onClick={() => toggleSpeaks(lang.code)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                            speaksLanguages.includes(lang.code)
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                          }`}
                          title="Vou falar neste idioma"
                        >
                          <Mic className="w-4 h-4" />
                          {speaksLanguages.includes(lang.code) && <Check className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {filteredLanguages.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  No languages found matching "{searchTerm}"
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-900/50 border-t border-gray-800 p-6">
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              disabled={saving}
              className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || speaksLanguages.length === 0 || understandsLanguages.length === 0}
              className="px-6 py-3 bg-gradient-to-r from-red-600 to-purple-600 text-white rounded-lg hover:from-red-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {saving ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Check className="w-5 h-5" />
                  Save Settings
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageConfigModal;
