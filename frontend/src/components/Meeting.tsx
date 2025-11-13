/**
 * Meeting Component - Premium UI
 * Main video conferencing interface with real-time translation
 */
import React, { useEffect, useRef, useState } from 'react';
import { useWebRTC } from '../hooks/useWebRTC';
import { useTranslation } from '../hooks/useTranslation';
import VideoGrid from './VideoGrid';
import ControlBar from './ControlBar';
import TranslationBar from './TranslationBar';
import LanguageSelector from './LanguageSelector';
import LanguageConfigModal from './LanguageConfigModal';
import { Copy, Check, Sparkles, Activity, Globe } from 'lucide-react';

interface MeetingProps {
  roomId: string;
  token: string;
  participants?: string[];
  language?: string;
  onLeave: () => void;
  userPreferences?: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    notifications: boolean;
    analytics: boolean;
  };
  connectionQuality?: 'excellent' | 'good' | 'fair' | 'poor';
}

const Meeting: React.FC<MeetingProps> = ({ roomId, token, onLeave }) => {
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [showLanguageConfig, setShowLanguageConfig] = useState(false);
  const [showCaptions, setShowCaptions] = useState(true);
  const [copied, setCopied] = useState(false);
  const [languageChanged, setLanguageChanged] = useState(false);
  const [speaksLanguages, setSpeaksLanguages] = useState<string[]>(['en']);
  const [understandsLanguages, setUnderstandsLanguages] = useState<string[]>(['en']);
  const [userName, setUserName] = useState<string>('');
  const [isHost, setIsHost] = useState<boolean>(false);
  const [isScreenSharing, setIsScreenSharing] = useState<boolean>(false);
  
  // WebRTC for video/audio
  const {
    localStream,
    participants: webrtcParticipants,
    isConnected: rtcConnected,
    isMuted,
    isVideoOff,
    error: rtcError,
    toggleMute,
    toggleVideo,
    startCall,
    endCall
  } = useWebRTC();
  
  // Translation WebSocket
  const {
    isConnected: translationConnected,
    inputLanguage,
    outputLanguage,
    lastTranslation,
    latency,
    error: translationError,
    connect: connectTranslation,
    disconnect: disconnectTranslation,
    sendAudioChunk,
    updateLanguages,
    mute: muteTranslation,
    unmute: unmuteTranslation
  } = useTranslation();
  
  const audioChunkInterval = useRef<number | null>(null);
  
  // Initialize call and translation on mount
  useEffect(() => {
    const initialize = async () => {
      try {
        // Start WebRTC call
        await startCall(roomId);
        
        // Connect translation WebSocket, passing current languages
        connectTranslation(roomId, token);
        
      } catch (err) {
        console.error('Failed to initialize meeting:', err);
      }
    };
    
    initialize();
    
    // Cleanup on unmount
    return () => {
      endCall();
      disconnectTranslation();
      if (audioChunkInterval.current) {
        clearInterval(audioChunkInterval.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId, token]); // Only re-run if roomId or token changes
  
  // Process audio chunks for translation
  useEffect(() => {
    if (!localStream || !translationConnected) return;
    
    const audioTrack = localStream.getAudioTracks()[0];
    if (!audioTrack) return;
    
    // Create media recorder to capture audio chunks
    // Try to use the most compatible format
    let mimeType = 'audio/webm';
    
    // Check for supported mimeTypes in order of preference
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4'
    ];
    
    for (const type of mimeTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type;
        console.log('📹 Using audio format:', type);
        break;
      }
    }
    
    const mediaRecorder = new MediaRecorder(new MediaStream([audioTrack]), {
      mimeType
    });
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        // Convert blob to ArrayBuffer and send
        event.data.arrayBuffer().then(buffer => {
          sendAudioChunk(buffer);
        });
      }
    };
    
    // Capture audio every 500ms for low latency
    mediaRecorder.start(500);
    
    return () => {
      mediaRecorder.stop();
    };
  }, [localStream, translationConnected, sendAudioChunk]);
  
  // Handle mute toggle (both audio and translation)
  const handleToggleMute = () => {
    toggleMute();
    if (isMuted) { // isMuted reflects the state *before* the toggle
      unmuteTranslation();
    } else {
      muteTranslation();
    }
  };
  
  // Handle language change
  const handleLanguageChange = (input: string, output: string) => {
    console.log('🔄 Meeting: Language change requested', { input, output });
    updateLanguages(input, output);
    setShowLanguageSelector(false);
    setLanguageChanged(true);
    setTimeout(() => setLanguageChanged(false), 3000);
    console.log('✅ Meeting: Language selector closed');
  };
  
  // Handle leave meeting
  const handleLeave = () => {
    endCall();
    disconnectTranslation();
    onLeave();
  };

  // Handle end meeting for all (host only)
  const handleEndMeeting = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      const response = await fetch(`http://localhost:8000/api/rooms/${roomId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        // Broadcast to all participants that meeting has ended
        endCall();
        disconnectTranslation();
        onLeave();
      }
    } catch (error) {
      console.error('Error ending meeting:', error);
    }
  };

  // Handle screen share toggle
  const handleToggleScreenShare = async () => {
    try {
      if (isScreenSharing) {
        // Stop screen sharing
        setIsScreenSharing(false);
        // Resume camera
        if (localStream) {
          const videoTrack = localStream.getVideoTracks()[0];
          if (videoTrack) {
            videoTrack.enabled = true;
          }
        }
      } else {
        // Start screen sharing
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: false
        });
        
        setIsScreenSharing(true);
        
        // Handle when user stops sharing via browser UI
        screenStream.getVideoTracks()[0].onended = () => {
          setIsScreenSharing(false);
        };
      }
    } catch (error) {
      console.error('Error toggling screen share:', error);
    }
  };
  
  const copyRoomLink = () => {
    const link = `${window.location.origin}?room=${roomId}`;
    navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Load user's language preferences and profile info
  useEffect(() => {
    const loadUserInfo = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        const response = await fetch('http://localhost:8000/api/profile/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setSpeaksLanguages(data.speaks_languages || ['en']);
          setUnderstandsLanguages(data.understands_languages || ['en']);
          setUserName(data.username || data.email || 'User');
        }
      } catch (error) {
        console.error('Error loading user info:', error);
      }
    };

    const checkIsHost = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        const response = await fetch(`http://localhost:8000/api/rooms/${roomId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          const userId = localStorage.getItem('user_id');
          setIsHost(data.created_by === userId);
        }
      } catch (error) {
        console.error('Error checking host status:', error);
      }
    };

    loadUserInfo();
    checkIsHost();
  }, [roomId]);

  // Handle save language preferences
  const handleSaveLanguages = async (speaks: string[], understands: string[]) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch('http://localhost:8000/api/profile/languages', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        speaks_languages: speaks,
        understands_languages: understands
      })
    });

    if (!response.ok) {
      throw new Error('Failed to save language settings');
    }

    const data = await response.json();
    setSpeaksLanguages(data.speaks_languages);
    setUnderstandsLanguages(data.understands_languages);
    
    // Update translation settings
    if (speaks.length > 0 && understands.length > 0) {
      updateLanguages(speaks[0], understands[0]);
    }
  };

  return (
    <div className="h-screen bg-gradient-to-r from-black via-black via-70% to-red-950/30 flex flex-col relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        <div className="absolute top-1/4 right-20 w-96 h-96 bg-red-400 rounded-full mix-blend-multiply filter blur-3xl opacity-15 animate-float" />
        <div className="absolute bottom-1/4 right-40 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl opacity-12 animate-float" style={{ animationDelay: '2s' }} />
      </div>
      {/* Header with room info and status */}
      <div className="glass-dark px-6 py-4 flex items-center justify-between relative z-10 backdrop-blur-xl border-b border-white/10">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-red-500 to-red-600 p-2 rounded-xl shadow-lg">
              <Sparkles size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold">Orbis Meeting</h1>
              <div className="flex items-center gap-2">
                <p className="text-gray-400 text-sm font-mono">{roomId}</p>
                <button
                  onClick={copyRoomLink}
                  className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-white/10 rounded"
                  title="Copy room link"
                >
                  {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Language Configuration Button */}
          <button
            onClick={() => setShowLanguageConfig(true)}
            className="glass px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-white/10 transition-all group"
            title="Configure Languages"
          >
            <Globe size={18} className="text-red-400 group-hover:text-red-300" />
            <span className="text-white text-sm font-medium">
              Languages ({speaksLanguages.length} / {understandsLanguages.length})
            </span>
          </button>

          {/* Connection status */}
          <div className="glass px-3 py-2 rounded-lg flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${rtcConnected ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`} />
            <span className="text-white text-sm font-medium">
              {rtcConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Translation status */}
          <div className="glass px-3 py-2 rounded-lg flex items-center gap-2">
            <Activity size={14} className={translationConnected ? 'text-red-400' : 'text-gray-400'} />
            <span className="text-white text-sm font-medium">
              {translationConnected ? 'Translating' : 'Inactive'}
            </span>
          </div>
          
          {/* Latency indicator */}
          {latency > 0 && (
            <div className="glass px-3 py-2 rounded-lg">
              <span className="text-gray-300 text-sm">
                <span className={latency < 200 ? 'text-red-400 font-bold' : 'text-yellow-400 font-bold'}>
                  {latency}ms
                </span>
              </span>
            </div>
          )}
        </div>
      </div>
      
      {/* Error messages */}
      {(rtcError || translationError) && (
        <div className="glass-dark border-l-4 border-red-500 bg-red-500/10 text-white px-6 py-3 animate-slide-down relative z-10">
          <p className="font-medium">⚠️ {rtcError || translationError}</p>
        </div>
      )}
      
      {/* Language changed notification */}
      {languageChanged && (
        <div className="glass-dark border-l-4 border-red-500 bg-red-500/10 text-white px-6 py-3 animate-slide-down relative z-10">
          <p className="font-medium">✅ Languages updated successfully!</p>
        </div>
      )}
      
      {/* Main video grid */}
      <div className="flex-1 relative z-10">
        <VideoGrid 
          localStream={localStream}
          participants={webrtcParticipants}
          isVideoOff={isVideoOff}
          userName={userName}
        />
        
        {/* Translation captions overlay */}
        {showCaptions && lastTranslation && (
          <div className="absolute bottom-24 left-1/2 transform -translate-x-1/2 glass-dark text-white px-8 py-4 rounded-2xl max-w-3xl shadow-2xl animate-slide-up border border-white/20">
            <p className="text-center text-lg leading-relaxed">{lastTranslation}</p>
          </div>
        )}
      </div>
      
      {/* Translation bar with language selection */}
      <div className="relative z-10">
        <TranslationBar
          inputLanguage={inputLanguage}
          outputLanguage={outputLanguage}
          onLanguageClick={() => setShowLanguageSelector(true)}
          onToggleCaptions={() => setShowCaptions(!showCaptions)}
          showCaptions={showCaptions}
        />
      </div>
      
      {/* Control bar */}
      <div className="relative z-10">
        <ControlBar
          isMuted={isMuted}
          isVideoOff={isVideoOff}
          onToggleMute={handleToggleMute}
          onToggleVideo={toggleVideo}
          onLeave={handleLeave}
          onEndMeeting={isHost ? handleEndMeeting : undefined}
          isHost={isHost}
          onToggleScreenShare={handleToggleScreenShare}
          isScreenSharing={isScreenSharing}
          participantCount={webrtcParticipants.size + 1}
        />
      </div>
      
      {/* Language selector modal */}
      {showLanguageSelector && (
        <div className="absolute inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowLanguageSelector(false)} />
          <div className="relative z-10 animate-scale-in">
            <LanguageSelector
              currentInput={inputLanguage}
              currentOutput={outputLanguage}
              onSave={handleLanguageChange}
              onClose={() => setShowLanguageSelector(false)}
            />
          </div>
        </div>
      )}

      {/* Language Configuration Modal */}
      <LanguageConfigModal
        isOpen={showLanguageConfig}
        onClose={() => setShowLanguageConfig(false)}
        currentSpeaksLanguages={speaksLanguages}
        currentUnderstandsLanguages={understandsLanguages}
        onSave={handleSaveLanguages}
      />
    </div>
  );
};

export default Meeting;
