"""
WebRTC Signaling Server
Handles WebSocket signaling for WebRTC connections
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from fastapi import WebSocket, WebSocketDisconnect

from sfu.mediasoup_worker import mediasoup_manager, Router, Transport, Producer
from sfu.config import sfu_config

logger = logging.getLogger(__name__)


@dataclass
class Participant:
    """Participant in a room"""
    participant_id: str
    user_id: Optional[str]
    websocket: WebSocket
    room_id: str
    joined_at: datetime = field(default_factory=datetime.utcnow)
    
    # WebRTC resources
    send_transport: Optional[Transport] = None
    recv_transport: Optional[Transport] = None
    producers: Dict[str, Producer] = field(default_factory=dict)
    consumers: Dict[str, 'Consumer'] = field(default_factory=dict)
    
    # User metadata
    display_name: Optional[str] = None
    audio_enabled: bool = True
    video_enabled: bool = True
    
    # Language preferences
    source_language: str = "en"
    target_languages: Set[str] = field(default_factory=lambda: {"en"})


class SignalingServer:
    """
    WebRTC Signaling Server
    Manages WebSocket connections and WebRTC signaling
    """
    
    def __init__(self):
        self.rooms: Dict[str, Set[str]] = {}  # room_id -> set of participant_ids
        self.participants: Dict[str, Participant] = {}  # participant_id -> Participant
        self.routers: Dict[str, Router] = {}  # room_id -> Router
        
        logger.info("🔌 Signaling server initialized")
    
    async def handle_connection(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: Optional[str] = None
    ):
        """
        Handle new WebSocket connection
        
        Args:
            websocket: FastAPI WebSocket connection
            room_id: Room to join
            user_id: Optional user ID
        """
        await websocket.accept()
        
        participant_id = str(uuid.uuid4())
        participant = Participant(
            participant_id=participant_id,
            user_id=user_id,
            websocket=websocket,
            room_id=room_id
        )
        
        self.participants[participant_id] = participant
        
        # Add to room
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(participant_id)
        
        # Create router if needed
        if room_id not in self.routers:
            router = await mediasoup_manager.create_router(room_id)
            if router:
                self.routers[room_id] = router
        
        logger.info(f"✅ Participant {participant_id} joined room {room_id}")
        
        # Send welcome message
        await self.send_message(websocket, {
            "type": "welcome",
            "participantId": participant_id,
            "roomId": room_id,
            "rtpCapabilities": self.get_rtp_capabilities()
        })
        
        # Notify other participants
        await self.broadcast_to_room(room_id, {
            "type": "participantJoined",
            "participantId": participant_id,
            "displayName": participant.display_name
        }, exclude=[participant_id])
        
        try:
            # Message handling loop
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await self.handle_message(participant, message)
                
        except WebSocketDisconnect:
            logger.info(f"👋 Participant {participant_id} disconnected")
        except Exception as e:
            logger.error(f"❌ Error handling participant {participant_id}: {e}")
        finally:
            await self.cleanup_participant(participant_id)
    
    async def handle_message(self, participant: Participant, message: Dict):
        """
        Handle signaling message
        
        Args:
            participant: Participant who sent message
            message: Message data
        """
        msg_type = message.get("type")
        
        try:
            if msg_type == "getRouterRtpCapabilities":
                await self.handle_get_rtp_capabilities(participant)
            
            elif msg_type == "createWebRtcTransport":
                await self.handle_create_transport(participant, message)
            
            elif msg_type == "connectWebRtcTransport":
                await self.handle_connect_transport(participant, message)
            
            elif msg_type == "produce":
                await self.handle_produce(participant, message)
            
            elif msg_type == "consume":
                await self.handle_consume(participant, message)
            
            elif msg_type == "setLanguages":
                await self.handle_set_languages(participant, message)
            
            elif msg_type == "pauseProducer":
                await self.handle_pause_producer(participant, message)
            
            elif msg_type == "resumeProducer":
                await self.handle_resume_producer(participant, message)
            
            elif msg_type == "pauseConsumer":
                await self.handle_pause_consumer(participant, message)
            
            elif msg_type == "resumeConsumer":
                await self.handle_resume_consumer(participant, message)
            
            else:
                logger.warning(f"⚠️ Unknown message type: {msg_type}")
        
        except Exception as e:
            logger.error(f"❌ Error handling message type {msg_type}: {e}")
            await self.send_error(participant.websocket, str(e))
    
    async def handle_get_rtp_capabilities(self, participant: Participant):
        """Send RTP capabilities to participant"""
        await self.send_message(participant.websocket, {
            "type": "routerRtpCapabilities",
            "rtpCapabilities": self.get_rtp_capabilities()
        })
    
    async def handle_create_transport(self, participant: Participant, message: Dict):
        """Create WebRTC transport"""
        direction = message.get("direction", "send")
        
        router = self.routers.get(participant.room_id)
        if not router:
            raise Exception("Router not found")
        
        transport = await mediasoup_manager.create_webrtc_transport(
            router=router,
            participant_id=participant.participant_id,
            direction=direction
        )
        
        if not transport:
            raise Exception("Failed to create transport")
        
        # Store transport
        if direction == "send":
            participant.send_transport = transport
        else:
            participant.recv_transport = transport
        
        # Send transport parameters
        await self.send_message(participant.websocket, {
            "type": "transportCreated",
            "direction": direction,
            "id": transport.transport_id,
            "iceParameters": transport.ice_parameters,
            "iceCandidates": transport.ice_candidates,
            "dtlsParameters": transport.dtls_parameters
        })
    
    async def handle_connect_transport(self, participant: Participant, message: Dict):
        """Connect WebRTC transport"""
        transport_id = message.get("transportId")
        dtls_parameters = message.get("dtlsParameters")
        
        # In production, call mediasoup's transport.connect()
        logger.info(f"🔗 Transport {transport_id} connected")
        
        await self.send_message(participant.websocket, {
            "type": "transportConnected",
            "transportId": transport_id
        })
    
    async def handle_produce(self, participant: Participant, message: Dict):
        """Handle media production (sending)"""
        kind = message.get("kind")
        rtp_parameters = message.get("rtpParameters")
        
        if not participant.send_transport:
            raise Exception("Send transport not created")
        
        producer = await mediasoup_manager.create_producer(
            transport=participant.send_transport,
            kind=kind,
            rtp_parameters=rtp_parameters
        )
        
        if not producer:
            raise Exception("Failed to create producer")
        
        participant.producers[producer.producer_id] = producer
        
        await self.send_message(participant.websocket, {
            "type": "produced",
            "kind": kind,
            "id": producer.producer_id
        })
        
        # Notify other participants about new producer
        await self.broadcast_to_room(participant.room_id, {
            "type": "newProducer",
            "participantId": participant.participant_id,
            "producerId": producer.producer_id,
            "kind": kind
        }, exclude=[participant.participant_id])
    
    async def handle_consume(self, participant: Participant, message: Dict):
        """Handle media consumption (receiving)"""
        producer_id = message.get("producerId")
        rtp_capabilities = message.get("rtpCapabilities")
        
        if not participant.recv_transport:
            raise Exception("Receive transport not created")
        
        # Find producer
        producer = None
        for p in self.participants.values():
            if producer_id in p.producers:
                producer = p.producers[producer_id]
                break
        
        if not producer:
            raise Exception("Producer not found")
        
        consumer = await mediasoup_manager.create_consumer(
            transport=participant.recv_transport,
            producer=producer,
            rtp_capabilities=rtp_capabilities
        )
        
        if not consumer:
            raise Exception("Failed to create consumer")
        
        participant.consumers[consumer.consumer_id] = consumer
        
        await self.send_message(participant.websocket, {
            "type": "consumed",
            "id": consumer.consumer_id,
            "producerId": producer_id,
            "kind": consumer.kind,
            "rtpParameters": consumer.rtp_parameters
        })
    
    async def handle_set_languages(self, participant: Participant, message: Dict):
        """Set participant language preferences"""
        source_lang = message.get("sourceLanguage")
        target_langs = message.get("targetLanguages", ["en"])
        
        if source_lang:
            participant.source_language = source_lang
        
        participant.target_languages = set(target_langs)
        
        logger.info(
            f"🌍 Participant {participant.participant_id} languages: "
            f"{source_lang} -> {target_langs}"
        )
        
        await self.send_message(participant.websocket, {
            "type": "languagesSet",
            "sourceLanguage": participant.source_language,
            "targetLanguages": list(participant.target_languages)
        })
    
    async def handle_pause_producer(self, participant: Participant, message: Dict):
        """Pause producer"""
        producer_id = message.get("producerId")
        if producer_id in participant.producers:
            participant.producers[producer_id].paused = True
            logger.info(f"⏸️ Producer {producer_id} paused")
    
    async def handle_resume_producer(self, participant: Participant, message: Dict):
        """Resume producer"""
        producer_id = message.get("producerId")
        if producer_id in participant.producers:
            participant.producers[producer_id].paused = False
            logger.info(f"▶️ Producer {producer_id} resumed")
    
    async def handle_pause_consumer(self, participant: Participant, message: Dict):
        """Pause consumer"""
        consumer_id = message.get("consumerId")
        if consumer_id in participant.consumers:
            participant.consumers[consumer_id].paused = True
            logger.info(f"⏸️ Consumer {consumer_id} paused")
    
    async def handle_resume_consumer(self, participant: Participant, message: Dict):
        """Resume consumer"""
        consumer_id = message.get("consumerId")
        if consumer_id in participant.consumers:
            participant.consumers[consumer_id].paused = False
            logger.info(f"▶️ Consumer {consumer_id} resumed")
    
    async def cleanup_participant(self, participant_id: str):
        """Clean up participant resources"""
        participant = self.participants.get(participant_id)
        if not participant:
            return
        
        # Close all producers
        for producer_id in list(participant.producers.keys()):
            await mediasoup_manager.close_producer(producer_id)
        
        # Close all consumers
        for consumer_id in list(participant.consumers.keys()):
            await mediasoup_manager.close_consumer(consumer_id)
        
        # Close transports
        if participant.send_transport:
            await mediasoup_manager.close_transport(participant.send_transport.transport_id)
        if participant.recv_transport:
            await mediasoup_manager.close_transport(participant.recv_transport.transport_id)
        
        # Remove from room
        if participant.room_id in self.rooms:
            self.rooms[participant.room_id].discard(participant_id)
            
            # Close router if room is empty
            if not self.rooms[participant.room_id]:
                if participant.room_id in self.routers:
                    await mediasoup_manager.close_router(
                        self.routers[participant.room_id].router_id
                    )
                    del self.routers[participant.room_id]
                del self.rooms[participant.room_id]
        
        # Notify others
        await self.broadcast_to_room(participant.room_id, {
            "type": "participantLeft",
            "participantId": participant_id
        })
        
        # Remove participant
        del self.participants[participant_id]
        
        logger.info(f"🧹 Participant {participant_id} cleaned up")
    
    async def send_message(self, websocket: WebSocket, message: Dict):
        """Send message to websocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
    
    async def send_error(self, websocket: WebSocket, error: str):
        """Send error message"""
        await self.send_message(websocket, {
            "type": "error",
            "error": error
        })
    
    async def broadcast_to_room(
        self,
        room_id: str,
        message: Dict,
        exclude: list = None
    ):
        """Broadcast message to all participants in room"""
        if room_id not in self.rooms:
            return
        
        exclude = exclude or []
        
        for participant_id in self.rooms[room_id]:
            if participant_id in exclude:
                continue
            
            participant = self.participants.get(participant_id)
            if participant:
                await self.send_message(participant.websocket, message)
    
    def get_rtp_capabilities(self) -> Dict:
        """Get router RTP capabilities"""
        # In production, get from mediasoup router
        return {
            "codecs": [
                {
                    "kind": "audio",
                    "mimeType": "audio/opus",
                    "clockRate": 48000,
                    "channels": 2,
                    "parameters": {
                        "useinbandfec": 1,
                        "usedtx": 1
                    }
                },
                {
                    "kind": "video",
                    "mimeType": "video/VP8",
                    "clockRate": 90000,
                    "parameters": {}
                },
                {
                    "kind": "video",
                    "mimeType": "video/H264",
                    "clockRate": 90000,
                    "parameters": {
                        "level-asymmetry-allowed": 1,
                        "packetization-mode": 1,
                        "profile-level-id": "42e01f"
                    }
                }
            ],
            "headerExtensions": [
                {
                    "kind": "audio",
                    "uri": "urn:ietf:params:rtp-hdrext:ssrc-audio-level",
                    "preferredId": 1
                },
                {
                    "kind": "video",
                    "uri": "http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time",
                    "preferredId": 4
                }
            ]
        }
    
    def get_stats(self) -> Dict:
        """Get signaling server statistics"""
        return {
            "rooms": len(self.rooms),
            "participants": len(self.participants),
            "mediasoup": mediasoup_manager.get_stats()
        }


# Singleton instance
signaling_server = SignalingServer()
