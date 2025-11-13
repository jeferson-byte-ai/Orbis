/**
 * useWebRTCSFU Hook - Simplified WebRTC with SFU
 * Wrapper around useMediasoupClient for easier integration
 */
import { useMemo } from 'react';
import { useMediasoupClient } from './useMediasoupClient';

interface UseWebRTCSFUProps {
  roomId: string;
  userId?: string;
  sourceLanguage?: string;
  targetLanguages?: string[];
  sfuUrl?: string;
}

export const useWebRTCSFU = ({
  roomId,
  userId,
  sourceLanguage = 'en',
  targetLanguages = ['en'],
  sfuUrl = 'ws://localhost:3000'
}: UseWebRTCSFUProps) => {
  
  const config = useMemo(() => ({
    sfuUrl,
    roomId,
    userId,
    sourceLanguage,
    targetLanguages
  }), [sfuUrl, roomId, userId, sourceLanguage, targetLanguages]);
  
  const {
    device,
    isConnected,
    localStream,
    participants,
    isMuted,
    isVideoOff,
    error,
    latency,
    connect,
    disconnect,
    toggleMute,
    toggleVideo,
    setLanguages
  } = useMediasoupClient(config);
  
  return {
    // Connection state
    device,
    isConnected,
    error,
    latency,
    
    // Media streams
    localStream,
    participants,
    
    // Controls
    isMuted,
    isVideoOff,
    toggleMute,
    toggleVideo,
    
    // Actions
    startCall: connect,
    endCall: disconnect,
    updateLanguages: setLanguages,
    
    // Compatibility with old useWebRTC interface
    participants: participants,
  };
};
