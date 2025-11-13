/**
 * Mediasoup Client Hook
 * Integrates with Orbis SFU Server using mediasoup-client
 * 
 * Install: npm install mediasoup-client
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import * as mediasoupClient from 'mediasoup-client';
import type { 
  Device,
  Transport,
  Producer,
  Consumer,
  RtpCapabilities
} from 'mediasoup-client/lib/types';

interface MediasoupConfig {
  sfuUrl: string;  // ws://localhost:3000
  roomId: string;
  userId?: string;
  sourceLanguage?: string;
  targetLanguages?: string[];
}

interface Participant {
  id: string;
  displayName?: string;
  audioConsumer?: Consumer;
  videoConsumer?: Consumer;
  audioEnabled: boolean;
  videoEnabled: boolean;
}

interface UseMediasoupReturn {
  device: Device | null;
  isConnected: boolean;
  localStream: MediaStream | null;
  participants: Map<string, Participant>;
  isMuted: boolean;
  isVideoOff: boolean;
  error: string | null;
  latency: number;
  connect: () => Promise<void>;
  disconnect: () => void;
  toggleMute: () => void;
  toggleVideo: () => void;
  setLanguages: (source: string, targets: string[]) => void;
}

export const useMediasoupClient = (config: MediasoupConfig): UseMediasoupReturn => {
  // State
  const [device, setDevice] = useState<Device | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [participants, setParticipants] = useState<Map<string, Participant>>(new Map());
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latency, setLatency] = useState(0);
  
  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const sendTransportRef = useRef<Transport | null>(null);
  const recvTransportRef = useRef<Transport | null>(null);
  const audioProducerRef = useRef<Producer | null>(null);
  const videoProducerRef = useRef<Producer | null>(null);
  const participantIdRef = useRef<string | null>(null);
  
  /**
   * Send message to signaling server
   */
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      console.log('📤 Sent:', message.type);
    }
  }, []);
  
  /**
   * Get user media (camera + microphone)
   */
  const getUserMedia = async (): Promise<MediaStream> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000,
          channelCount: 2
        },
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30 }
        }
      });
      
      setLocalStream(stream);
      return stream;
    } catch (err) {
      throw new Error(`Failed to get user media: ${err}`);
    }
  };
  
  /**
   * Create send transport
   */
  const createSendTransport = async (device: Device) => {
    console.log('🚀 Creating send transport...');
    
    return new Promise<Transport>((resolve, reject) => {
      // Request transport from server
      sendMessage({ type: 'createWebRtcTransport', direction: 'send' });
      
      // Listen for transport created event
      const handler = (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'transportCreated' && data.direction === 'send') {
          wsRef.current?.removeEventListener('message', handler);
          
          // Create transport
          device.createSendTransport({
            id: data.id,
            iceParameters: data.iceParameters,
            iceCandidates: data.iceCandidates,
            dtlsParameters: data.dtlsParameters
          }).then(transport => {
            console.log('✅ Send transport created');
            
            // Handle connect event
            transport.on('connect', async ({ dtlsParameters }, callback, errback) => {
              try {
                sendMessage({
                  type: 'connectWebRtcTransport',
                  transportId: transport.id,
                  dtlsParameters
                });
                callback();
              } catch (err) {
                errback(err as Error);
              }
            });
            
            // Handle produce event
            transport.on('produce', async ({ kind, rtpParameters }, callback, errback) => {
              try {
                // Send produce request
                sendMessage({
                  type: 'produce',
                  kind,
                  rtpParameters
                });
                
                // Wait for response
                const produceHandler = (event: MessageEvent) => {
                  const data = JSON.parse(event.data);
                  if (data.type === 'produced' && data.kind === kind) {
                    wsRef.current?.removeEventListener('message', produceHandler);
                    callback({ id: data.id });
                  }
                };
                wsRef.current?.addEventListener('message', produceHandler);
                
              } catch (err) {
                errback(err as Error);
              }
            });
            
            sendTransportRef.current = transport;
            resolve(transport);
          }).catch(reject);
        }
      };
      
      wsRef.current?.addEventListener('message', handler);
    });
  };
  
  /**
   * Create receive transport
   */
  const createRecvTransport = async (device: Device) => {
    console.log('🚀 Creating recv transport...');
    
    return new Promise<Transport>((resolve, reject) => {
      // Request transport from server
      sendMessage({ type: 'createWebRtcTransport', direction: 'recv' });
      
      // Listen for transport created event
      const handler = (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'transportCreated' && data.direction === 'recv') {
          wsRef.current?.removeEventListener('message', handler);
          
          // Create transport
          device.createRecvTransport({
            id: data.id,
            iceParameters: data.iceParameters,
            iceCandidates: data.iceCandidates,
            dtlsParameters: data.dtlsParameters
          }).then(transport => {
            console.log('✅ Recv transport created');
            
            // Handle connect event
            transport.on('connect', async ({ dtlsParameters }, callback, errback) => {
              try {
                sendMessage({
                  type: 'connectWebRtcTransport',
                  transportId: transport.id,
                  dtlsParameters
                });
                callback();
              } catch (err) {
                errback(err as Error);
              }
            });
            
            recvTransportRef.current = transport;
            resolve(transport);
          }).catch(reject);
        }
      };
      
      wsRef.current?.addEventListener('message', handler);
    });
  };
  
  /**
   * Produce media (audio/video)
   */
  const produceMedia = async (transport: Transport, stream: MediaStream) => {
    console.log('🎙️ Producing media...');
    
    // Produce audio
    const audioTrack = stream.getAudioTracks()[0];
    if (audioTrack) {
      const audioProducer = await transport.produce({
        track: audioTrack,
        codecOptions: {
          opusStereo: true,
          opusDtx: true,
          opusFec: true
        }
      });
      audioProducerRef.current = audioProducer;
      console.log('✅ Audio producer created:', audioProducer.id);
    }
    
    // Produce video
    const videoTrack = stream.getVideoTracks()[0];
    if (videoTrack) {
      const videoProducer = await transport.produce({
        track: videoTrack,
        codecOptions: {
          videoGoogleStartBitrate: 1000
        }
      });
      videoProducerRef.current = videoProducer;
      console.log('✅ Video producer created:', videoProducer.id);
    }
  };
  
  /**
   * Consume media from remote producer
   */
  const consumeMedia = async (
    transport: Transport,
    producerId: string,
    kind: 'audio' | 'video',
    rtpCapabilities: RtpCapabilities
  ) => {
    console.log(`🔽 Consuming ${kind}...`);
    
    return new Promise<Consumer>((resolve, reject) => {
      sendMessage({
        type: 'consume',
        producerId,
        rtpCapabilities
      });
      
      const handler = (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'consumed' && data.producerId === producerId) {
          wsRef.current?.removeEventListener('message', handler);
          
          transport.consume({
            id: data.id,
            producerId: data.producerId,
            kind: data.kind,
            rtpParameters: data.rtpParameters
          }).then(consumer => {
            console.log(`✅ ${kind} consumer created:`, consumer.id);
            resolve(consumer);
          }).catch(reject);
        }
      };
      
      wsRef.current?.addEventListener('message', handler);
    });
  };
  
  /**
   * Handle WebSocket messages
   */
  const handleMessage = useCallback(async (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    console.log('📥 Received:', data.type);
    
    switch (data.type) {
      case 'welcome':
        participantIdRef.current = data.participantId;
        console.log('👋 Welcome! Participant ID:', data.participantId);
        console.log('RTP Capabilities received');
        break;
      
      case 'participantJoined':
        console.log('👤 Participant joined:', data.participantId);
        setParticipants(prev => new Map(prev).set(data.participantId, {
          id: data.participantId,
          displayName: data.displayName,
          audioEnabled: true,
          videoEnabled: true
        }));
        break;
      
      case 'participantLeft':
        console.log('👋 Participant left:', data.participantId);
        setParticipants(prev => {
          const next = new Map(prev);
          next.delete(data.participantId);
          return next;
        });
        break;
      
      case 'newProducer':
        console.log('🎬 New producer:', data.producerId, data.kind);
        // In a full implementation, consume this producer
        break;
      
      case 'translatedAudio':
        console.log('🌍 Translated audio received:', data.language);
        // Handle translated audio
        break;
      
      case 'error':
        console.error('❌ Error from server:', data.error);
        setError(data.error);
        break;
    }
  }, []);
  
  /**
   * Connect to SFU
   */
  const connect = useCallback(async () => {
    try {
      console.log('🚀 Connecting to SFU...');
      setError(null);
      
      // Create WebSocket connection
      const wsUrl = `${config.sfuUrl}/ws/${config.roomId}${config.userId ? `?user_id=${config.userId}` : ''}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      // WebSocket event handlers
      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };
      
      ws.onmessage = handleMessage;
      
      ws.onerror = (err) => {
        console.error('❌ WebSocket error:', err);
        setError('WebSocket connection failed');
      };
      
      ws.onclose = () => {
        console.log('👋 WebSocket closed');
        setIsConnected(false);
      };
      
      // Wait for welcome message with RTP capabilities
      await new Promise<RtpCapabilities>((resolve) => {
        const handler = (event: MessageEvent) => {
          const data = JSON.parse(event.data);
          if (data.type === 'welcome') {
            ws.removeEventListener('message', handler);
            resolve(data.rtpCapabilities);
          }
        };
        ws.addEventListener('message', handler);
      });
      
      // Create mediasoup device
      const newDevice = new mediasoupClient.Device();
      await newDevice.load({ 
        routerRtpCapabilities: await new Promise<RtpCapabilities>((resolve) => {
          sendMessage({ type: 'getRouterRtpCapabilities' });
          const handler = (event: MessageEvent) => {
            const data = JSON.parse(event.data);
            if (data.type === 'routerRtpCapabilities') {
              ws.removeEventListener('message', handler);
              resolve(data.rtpCapabilities);
            }
          };
          ws.addEventListener('message', handler);
        })
      });
      setDevice(newDevice);
      console.log('✅ Device loaded');
      
      // Get user media
      const stream = await getUserMedia();
      
      // Create transports
      const sendTransport = await createSendTransport(newDevice);
      const recvTransport = await createRecvTransport(newDevice);
      
      // Produce media
      await produceMedia(sendTransport, stream);
      
      // Set languages
      if (config.sourceLanguage && config.targetLanguages) {
        sendMessage({
          type: 'setLanguages',
          sourceLanguage: config.sourceLanguage,
          targetLanguages: config.targetLanguages
        });
      }
      
      setIsConnected(true);
      console.log('✅ Connected to SFU');
      
    } catch (err) {
      console.error('❌ Connection failed:', err);
      setError(`Connection failed: ${err}`);
    }
  }, [config, handleMessage, sendMessage]);
  
  /**
   * Disconnect from SFU
   */
  const disconnect = useCallback(() => {
    console.log('👋 Disconnecting...');
    
    // Close producers
    audioProducerRef.current?.close();
    videoProducerRef.current?.close();
    
    // Close transports
    sendTransportRef.current?.close();
    recvTransportRef.current?.close();
    
    // Stop local tracks
    localStream?.getTracks().forEach(track => track.stop());
    
    // Close WebSocket
    wsRef.current?.close();
    
    // Reset state
    setIsConnected(false);
    setLocalStream(null);
    setParticipants(new Map());
    
    console.log('✅ Disconnected');
  }, [localStream]);
  
  /**
   * Toggle mute
   */
  const toggleMute = useCallback(() => {
    const producer = audioProducerRef.current;
    if (!producer) return;
    
    if (isMuted) {
      producer.resume();
      setIsMuted(false);
      console.log('🔊 Unmuted');
    } else {
      producer.pause();
      setIsMuted(true);
      console.log('🔇 Muted');
    }
  }, [isMuted]);
  
  /**
   * Toggle video
   */
  const toggleVideo = useCallback(() => {
    const producer = videoProducerRef.current;
    if (!producer) return;
    
    if (isVideoOff) {
      producer.resume();
      setIsVideoOff(false);
      console.log('📹 Video on');
    } else {
      producer.pause();
      setIsVideoOff(true);
      console.log('📴 Video off');
    }
  }, [isVideoOff]);
  
  /**
   * Set languages
   */
  const setLanguages = useCallback((source: string, targets: string[]) => {
    sendMessage({
      type: 'setLanguages',
      sourceLanguage: source,
      targetLanguages: targets
    });
    console.log('🌍 Languages set:', { source, targets });
  }, [sendMessage]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);
  
  return {
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
  };
};
