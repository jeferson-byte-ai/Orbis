/**
 * ThreeDInterface Component
 * Revolutionary 3D interface for immersive user experience
 */
import React, { useRef, useEffect, useState } from 'react';

interface ThreeDInterfaceProps {
  participants: Array<{
    id: string;
    name: string;
    language: string;
    isSpeaking: boolean;
    position: { x: number; y: number; z: number };
  }>;
  onParticipantClick: (participantId: string) => void;
  className?: string;
}

const ThreeDInterface: React.FC<ThreeDInterfaceProps> = ({
  participants,
  onParticipantClick,
  className = ''
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Three.js will be implemented when the library is installed
    setIsLoaded(true);
  }, [participants, onParticipantClick]);

  const getLanguageColor = (language: string): string => {
    const colors: { [key: string]: string } = {
      'en': '#3B82F6',
      'es': '#10B981',
      'fr': '#8B5CF6',
      'de': '#F59E0B',
      'pt': '#EF4444',
      'it': '#06B6D4',
      'ja': '#84CC16',
      'ko': '#F97316',
      'zh': '#EC4899',
      'ru': '#6366F1'
    };
    return colors[language] || '#6B7280';
  };

  return (
    <div 
      ref={mountRef} 
      className={`orbis-3d-interface ${className}`}
      style={{
        width: '100%',
        height: '100%',
        background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
        borderRadius: 'var(--orbis-radius-xl)',
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      {/* Placeholder for 3D interface */}
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-6xl mb-4">🌍</div>
          <h3 className="text-xl font-semibold text-white mb-2">
            3D Interface
          </h3>
          <p className="text-gray-400 mb-4">
            Immersive 3D meeting space
          </p>
          <div className="text-sm text-gray-500">
            {participants.length} participants
          </div>
        </div>
      </div>

      {/* Participant indicators */}
      <div className="absolute top-4 left-4 space-y-2">
        {participants.map((participant) => (
          <div
            key={participant.id}
            className="flex items-center gap-2 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 cursor-pointer hover:bg-black/70 transition-colors"
            onClick={() => onParticipantClick(participant.id)}
          >
            <div
              className="w-3 h-3 rounded-full"
              style={{
                backgroundColor: getLanguageColor(participant.language),
                boxShadow: participant.isSpeaking ? '0 0 10px currentColor' : 'none'
              }}
            />
            <span className="text-white text-sm font-medium">
              {participant.name}
            </span>
            {participant.isSpeaking && (
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
            )}
          </div>
        ))}
      </div>

      {/* Status indicator */}
      <div className="absolute bottom-4 right-4">
        <div className="flex items-center gap-2 bg-green-500/20 backdrop-blur-sm rounded-lg px-3 py-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-green-400 text-sm font-medium">
            {isLoaded ? 'Ready' : 'Loading...'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ThreeDInterface;