/**
 * Orbis Description Page
 * Detailed explanation of Orbis's platform and capabilities
 */
import React from 'react';
import { Mic, Volume2, Languages, Zap, Users, Globe, Video, Clock, Briefcase, Building, MessageSquare, CheckCircle, ArrowRight } from 'lucide-react';

const TranslationDemo: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Header */}
      <div className="glass-dark px-6 py-4 border-b border-white/10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-xl">
              <Languages size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold">How Orbis Works</h1>
              <p className="text-sm text-gray-400">Multilingual Meeting Platform</p>
            </div>
          </div>
          <a href="/" className="glass px-4 py-2 rounded-lg hover:bg-white/10 transition-colors">
            Back
          </a>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Hero Section - Main Description */}
        <div className="glass-dark rounded-2xl p-8 mb-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-2xl">
              <Globe size={32} />
            </div>
            <div>
              <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                What is Orbis?
              </h2>
              <p className="text-lg text-gray-300 leading-relaxed">
                <strong className="text-white">Orbis</strong> is an online meeting platform that allows users to communicate 
                instantly in different languages. It combines <span className="text-purple-400 font-semibold">real-time translation</span> with{' '}
                <span className="text-pink-400 font-semibold">voice cloning</span>, providing a natural and fluid experience. 
              </p>
            </div>
          </div>
        </div>

        {/* Target Audience */}
        <div className="glass-dark rounded-2xl p-8 mb-6">
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Users size={28} className="text-blue-400" />
            Target Audience
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="glass rounded-xl p-6 border border-blue-500/20 hover:border-blue-500/50 transition-all">
              <div className="bg-blue-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Briefcase size={24} className="text-blue-400" />
              </div>
              <h4 className="font-bold text-lg mb-2">International Professionals</h4>
              <p className="text-gray-400 text-sm">
                Ideal for professionals who participate in international meetings and need to communicate in multiple languages.
              </p>
            </div>

            <div className="glass rounded-xl p-6 border border-green-500/20 hover:border-green-500/50 transition-all">
              <div className="bg-green-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Building size={24} className="text-green-400" />
              </div>
              <h4 className="font-bold text-lg mb-2">Global Companies</h4>
              <p className="text-gray-400 text-sm">
                Companies that work with global teams and require effective communication across different cultures.
              </p>
            </div>

            <div className="glass rounded-xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all">
              <div className="bg-purple-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <MessageSquare size={24} className="text-purple-400" />
              </div>
              <h4 className="font-bold text-lg mb-2">Instant Communication</h4>
              <p className="text-gray-400 text-sm">
                Users who need instant communication in multiple languages without language barriers.
              </p>
            </div>
          </div>
        </div>

        {/* Main Features */}
        <div className="glass-dark rounded-2xl p-8 mb-6">
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Zap size={28} className="text-yellow-400" />
            Main Features
          </h3>
          <div className="space-y-4">
            {/* Feature 1 */}
            <div className="glass rounded-xl p-6 flex items-start gap-4 hover:bg-white/5 transition-all">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-lg flex-shrink-0">
                <Video size={24} />
              </div>
              <div>
                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                  Multilingual Meetings
                  <CheckCircle size={18} className="text-green-400" />
                </h4>
                <p className="text-gray-300">
                  Support for individual or group meetings with participants from different languages. Everyone can speak 
                  in their native language and be understood by all other participants.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="glass rounded-xl p-6 flex items-start gap-4 hover:bg-white/5 transition-all">
              <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-3 rounded-lg flex-shrink-0">
                <Languages size={24} />
              </div>
              <div>
                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                  Simultaneous Translation
                  <CheckCircle size={18} className="text-green-400" />
                </h4>
                <p className="text-gray-300">
                  Automatic real-time voice translation using advanced AI models (NLLB-200). Support for 
                  over 200 languages with high accuracy and naturalness.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="glass rounded-xl p-6 flex items-start gap-4 hover:bg-white/5 transition-all">
              <div className="bg-gradient-to-br from-pink-500 to-red-500 p-3 rounded-lg flex-shrink-0">
                <Volume2 size={24} />
              </div>
              <div>
                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                  Voice Cloning
                  <CheckCircle size={18} className="text-green-400" />
                </h4>
                <p className="text-gray-300">
                  Each user's voice is cloned to maintain timbre and intonation during translation, functioning as 
                  natural dubbing. Your vocal personality is preserved, even in another language.
                </p>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="glass rounded-xl p-6 flex items-start gap-4 hover:bg-white/5 transition-all">
              <div className="bg-gradient-to-br from-green-500 to-emerald-500 p-3 rounded-lg flex-shrink-0">
                <Clock size={24} />
              </div>
              <div>
                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                  Low Latency
                  <CheckCircle size={18} className="text-green-400" />
                </h4>
                <p className="text-gray-300">
                  Near-instant communication with target latency below 250ms, ensuring fluid and natural meetings. 
                  The technology ensures conversation flows without noticeable interruptions.
                </p>
              </div>
            </div>

            {/* Feature 5 */}
            <div className="glass rounded-xl p-6 flex items-start gap-4 hover:bg-white/5 transition-all">
              <div className="bg-gradient-to-br from-orange-500 to-yellow-500 p-3 rounded-lg flex-shrink-0">
                <Zap size={24} />
              </div>
              <div>
                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                  Intuitive Interface
                  <CheckCircle size={18} className="text-green-400" />
                </h4>
                <p className="text-gray-300">
                  Easy to use, with features similar to popular video conferencing apps. Modern 
                  and responsive interface that works on any device.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Use Case Example */}
        <div className="glass-dark rounded-2xl p-8">
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <MessageSquare size={28} className="text-pink-400" />
            Use Case Example
          </h3>
          <div className="glass rounded-xl p-6 border border-purple-500/30">
            <div className="flex items-start gap-4 mb-6">
              <div className="bg-blue-500 p-3 rounded-full flex-shrink-0">
                <Users size={24} />
              </div>
              <div>
                <h4 className="font-bold text-lg mb-2">Scenario: International Meeting</h4>
                <p className="text-gray-300">
                  A Brazilian user who speaks Portuguese needs to meet with American colleagues who speak English.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {/* User 1 speaks */}
              <div className="flex items-start gap-3">
                <div className="bg-blue-500/20 rounded-lg p-4 flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-bold text-blue-400">🇧🇷 Brazilian User</span>
                  </div>
                  <p className="text-gray-300 mb-2">"Hello! Let's discuss the project?"</p>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <ArrowRight size={16} />
                    <span>Orbis translates and clones the voice</span>
                  </div>
                </div>
              </div>

              {/* Translation happens */}
              <div className="flex items-center justify-center">
                <div className="glass rounded-full px-6 py-2 flex items-center gap-2">
                  <Languages size={16} className="text-purple-400" />
                  <span className="text-sm text-gray-400">Real-Time Translation</span>
                  <Zap size={16} className="text-yellow-400" />
                </div>
              </div>

              {/* User 2 hears */}
              <div className="flex items-start gap-3">
                <div className="bg-green-500/20 rounded-lg p-4 flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-bold text-green-400">🇺🇸 American User Hears</span>
                  </div>
                  <p className="text-gray-300 mb-2">"Hello! Let's discuss the project?"</p>
                  <div className="flex items-center gap-2 text-sm text-purple-400">
                    <Volume2 size={16} />
                    <span>With the Brazilian's cloned voice</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-white/10">
              <p className="text-center text-gray-300">
                <strong className="text-purple-400">Result:</strong> Both participants communicate naturally in their native languages, 
                hearing the translations with the cloned original voices. The meeting flows completely understandable and natural for everyone!
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-6 text-center glass-dark rounded-2xl p-8">
          <h3 className="text-2xl font-bold mb-3">Ready to Break Language Barriers?</h3>
          <p className="text-gray-400 mb-6">
            Try Orbis and revolutionize your international meetings with real-time translation and voice cloning.
          </p>
          <a 
            href="/" 
            className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-8 py-3 rounded-xl font-bold text-lg transition-all shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95"
          >
            Get Started Now
            <ArrowRight size={20} />
          </a>
        </div>
      </div>
    </div>
  );
};

export default TranslationDemo;
