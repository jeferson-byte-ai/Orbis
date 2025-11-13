/**
 * Main App Component - BILLION DOLLAR EDITION
 * Revolutionary multilingual communication platform
 */
import React, { useState, useEffect } from 'react';
import Meeting from './components/Meeting';
import Home from './pages/Home';
import VoiceCloneOnboarding from './pages/VoiceCloneOnboarding';
import ParticleBackground from './components/ParticleBackground';
import LoadingScreen from './components/LoadingScreen';
import NotificationSystem from './components/NotificationSystem';
import AnalyticsTracker from './components/AnalyticsTracker';

type AppState = 'loading' | 'home' | 'onboarding' | 'meeting';

interface MeetingData {
  roomId: string;
  token: string;
  participants?: string[];
  language?: string;
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: boolean;
  analytics: boolean;
}

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('loading');
  const [meetingData, setMeetingData] = useState<MeetingData | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    theme: 'auto',
    language: 'en',
    notifications: true,
    analytics: true
  });
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionQuality, setConnectionQuality] = useState<'excellent' | 'good' | 'fair' | 'poor'>('excellent');

  // Initialize app
  useEffect(() => {
    initializeApp();
    setupEventListeners();
    checkConnectionQuality();
  }, []);

  // Monitor connection quality
  useEffect(() => {
    const interval = setInterval(checkConnectionQuality, 5000);
    return () => clearInterval(interval);
  }, []);

  const initializeApp = async () => {
    try {
      // Load user preferences
      const savedPreferences = localStorage.getItem('orbis_preferences');
      if (savedPreferences) {
        setUserPreferences(JSON.parse(savedPreferences));
      }

      // Check for voice profile
      // const hasVoiceProfile = localStorage.getItem('hasVoiceProfile') === 'true';
      
      // Simulate loading time for better UX
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setAppState('home');
    } catch (error) {
      console.error('Failed to initialize app:', error);
      setAppState('home');
    }
  };

  const setupEventListeners = () => {
    // Online/offline detection
    window.addEventListener('online', () => setIsOnline(true));
    window.addEventListener('offline', () => setIsOnline(false));

    // Connection quality monitoring
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', checkConnectionQuality);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
  };

  const checkConnectionQuality = () => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const downlink = connection.downlink || 10;
      const rtt = connection.rtt || 50;
      
      if (downlink > 5 && rtt < 100) {
        setConnectionQuality('excellent');
      } else if (downlink > 2 && rtt < 200) {
        setConnectionQuality('good');
      } else if (downlink > 1 && rtt < 500) {
        setConnectionQuality('fair');
      } else {
        setConnectionQuality('poor');
      }
    }
  };

  const handleKeyboardShortcuts = (event: KeyboardEvent) => {
    // Ctrl/Cmd + K for quick meeting join
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
      event.preventDefault();
      // Focus on meeting join input
      const joinInput = document.querySelector('[data-join-meeting]') as HTMLInputElement;
      if (joinInput) {
        joinInput.focus();
      }
    }
    
    // Escape to leave meeting
    if (event.key === 'Escape' && appState === 'meeting') {
      handleLeaveMeeting();
    }
  };

  const handleJoinMeeting = (roomId: string, token: string, participants?: string[], language?: string) => {
            // Check if user has completed voice cloning
            // const hasVoiceProfile = localStorage.getItem('hasVoiceProfile') === 'true';
    
    setMeetingData({ roomId, token, participants, language });
    
    // Track analytics
    if (userPreferences.analytics) {
      AnalyticsTracker.getInstance().track('meeting_join_attempted', {
        roomId,
        hasVoiceProfile: localStorage.getItem('hasVoiceProfile') === 'true',
        connectionQuality,
        timestamp: new Date().toISOString()
      });
    }
    
    const hasVoiceProfile = localStorage.getItem('hasVoiceProfile') === 'true';
    if (!hasVoiceProfile) {
      // First time user - go to onboarding
      setAppState('onboarding');
    } else {
      // User has voice profile - go directly to meeting
      setAppState('meeting');
    }
  };
  
  const handleOnboardingComplete = () => {
    localStorage.setItem('hasVoiceProfile', 'true');
    
    // Track analytics
    if (userPreferences.analytics) {
      AnalyticsTracker.getInstance().track('voice_profile_created', {
        timestamp: new Date().toISOString()
      });
    }
    
    setAppState('meeting');
  };
  
  const handleLeaveMeeting = () => {
    // Track analytics
    if (userPreferences.analytics && meetingData) {
      AnalyticsTracker.getInstance().track('meeting_left', {
        roomId: meetingData.roomId,
        timestamp: new Date().toISOString()
      });
    }
    
    setAppState('home');
    setMeetingData(null);
  };

  const updateUserPreferences = (newPreferences: Partial<UserPreferences>) => {
    const updated = { ...userPreferences, ...newPreferences };
    setUserPreferences(updated);
    localStorage.setItem('orbis_preferences', JSON.stringify(updated));
  };

  // Show loading screen
  if (appState === 'loading') {
    return <LoadingScreen />;
  }

  return (
    <div className="app" data-theme={userPreferences.theme}>
      {/* Particle Background */}
      <ParticleBackground />
      
      {/* Connection Status Indicator */}
      {!isOnline && (
        <div className="fixed top-4 right-4 z-50 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span>Offline</span>
          </div>
        </div>
      )}
      
      {/* Connection Quality Indicator */}
      {isOnline && connectionQuality !== 'excellent' && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-2 rounded-lg shadow-lg ${
          connectionQuality === 'good' ? 'bg-yellow-500' : 
          connectionQuality === 'fair' ? 'bg-orange-500' : 'bg-red-500'
        } text-white`}>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              connectionQuality === 'good' ? 'bg-white' : 
              connectionQuality === 'fair' ? 'bg-white' : 'bg-white animate-pulse'
            }`}></div>
            <span className="capitalize">{connectionQuality} Connection</span>
          </div>
        </div>
      )}

      {/* Notification System */}
      <NotificationSystem />
      
      {/* Main App Content */}
      <div className="relative z-10">
        {appState === 'home' && (
          <Home 
            onJoinMeeting={handleJoinMeeting}
            userPreferences={userPreferences}
            onUpdatePreferences={updateUserPreferences}
            connectionQuality={connectionQuality}
          />
        )}
        
        {appState === 'onboarding' && meetingData && (
          <VoiceCloneOnboarding
            onComplete={handleOnboardingComplete}
            onSkip={() => setAppState('meeting')}
            userPreferences={userPreferences}
          />
        )}
        
        {appState === 'meeting' && meetingData && (
          <Meeting
            roomId={meetingData.roomId}
            token={meetingData.token}
            participants={meetingData.participants}
            language={meetingData.language}
            onLeave={handleLeaveMeeting}
            userPreferences={userPreferences}
            connectionQuality={connectionQuality}
          />
        )}
      </div>
    </div>
  );
};

export default App;