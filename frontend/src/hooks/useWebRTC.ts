/**
 * useWebRTC Hook
 * Manages WebRTC connections for video/audio streaming
 */
import { useState, useEffect, useRef, useCallback } from 'react';

interface Participant {
  id: string;
  stream: MediaStream | null;
  isMuted: boolean;
  isVideoOff: boolean;
  language: string;
}

interface UseWebRTCReturn {
  localStream: MediaStream | null;
  participants: Map<string, Participant>;
  isConnected: boolean;
  isMuted: boolean;
  isVideoOff: boolean;
  error: string | null;
  toggleMute: () => void;
  toggleVideo: () => void;
  startCall: (roomId: string) => Promise<void>;
  endCall: () => void;
}

export const useWebRTC = (): UseWebRTCReturn => {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [participants, setParticipants] = useState<Map<string, Participant>>(new Map());
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const peerConnections = useRef<Map<string, RTCPeerConnection>>(new Map());
  
  // Get user media (camera + microphone)
  const getUserMedia = async (): Promise<MediaStream> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          frameRate: { ideal: 30 }
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000
        }
      });
      
      setLocalStream(stream);
      return stream;
    } catch (err) {
      const errorMsg = `Failed to access camera/microphone: ${err}`;
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  };
  
  // Toggle mute/unmute
  const toggleMute = useCallback(() => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMuted(!audioTrack.enabled);
      }
    }
  }, [localStream]);
  
  // Toggle video on/off
  const toggleVideo = useCallback(() => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoOff(!videoTrack.enabled);
      }
    }
  }, [localStream]);
  
  // Start WebRTC call
  const startCall = useCallback(async (roomId: string) => {
    try {
      await getUserMedia();
      setIsConnected(true);
      setError(null);
      
      // In production, this would:
      // 1. Connect to signaling server
      // 2. Exchange SDP offers/answers
      // 3. Establish peer connections
      console.log(`Starting call in room: ${roomId}`);
      
    } catch (err) {
      setError(`Failed to start call: ${err}`);
      console.error('Call start error:', err);
    }
  }, []);
  
  // End WebRTC call
  const endCall = useCallback(() => {
    // Stop all tracks
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      setLocalStream(null);
    }
    
    // Close all peer connections
    peerConnections.current.forEach(pc => pc.close());
    peerConnections.current.clear();
    
    setParticipants(new Map());
    setIsConnected(false);
    setIsMuted(false);
    setIsVideoOff(false);
  }, [localStream]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      endCall();
    };
  }, [endCall]);
  
  return {
    localStream,
    participants,
    isConnected,
    isMuted,
    isVideoOff,
    error,
    toggleMute,
    toggleVideo,
    startCall,
    endCall
  };
};