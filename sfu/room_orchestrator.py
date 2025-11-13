"""
Room Orchestrator
Manages real-time audio streaming and ML processing for rooms
"""
import asyncio
import logging
import time
import numpy as np
from typing import Dict, Optional, Set
from collections import defaultdict

from sfu.ml_pipeline import ml_pipeline, AudioChunk
from sfu.signaling_server import signaling_server
from sfu.config import sfu_config

logger = logging.getLogger(__name__)


class RoomOrchestrator:
    """
    Orchestrates real-time audio streaming and ML processing
    
    Flow:
    1. Receive audio from participant A (language X)
    2. Process through ML pipeline (ASR -> MT -> TTS)
    3. Send translated audio to participants B, C, D (languages Y, Z)
    4. All in real-time with <150ms latency
    """
    
    def __init__(self):
        self.active_rooms: Set[str] = set()
        self.audio_queues: Dict[str, asyncio.Queue] = {}  # room_id -> audio queue
        self.processing_tasks: Dict[str, asyncio.Task] = {}  # room_id -> processing task
        
        # Performance metrics
        self.processed_chunks = 0
        self.total_latency_ms = 0
        
        logger.info("🎭 Room orchestrator initialized")
    
    async def start_room(self, room_id: str):
        """Start audio processing for a room"""
        if room_id in self.active_rooms:
            logger.info(f"Room {room_id} already active")
            return
        
        self.active_rooms.add(room_id)
        self.audio_queues[room_id] = asyncio.Queue(maxsize=100)
        
        # Start processing task
        task = asyncio.create_task(self._process_room_audio(room_id))
        self.processing_tasks[room_id] = task
        
        logger.info(f"✅ Room {room_id} started")
    
    async def stop_room(self, room_id: str):
        """Stop audio processing for a room"""
        if room_id not in self.active_rooms:
            return
        
        self.active_rooms.discard(room_id)
        
        # Cancel processing task
        if room_id in self.processing_tasks:
            self.processing_tasks[room_id].cancel()
            try:
                await self.processing_tasks[room_id]
            except asyncio.CancelledError:
                pass
            del self.processing_tasks[room_id]
        
        # Clean up queue
        if room_id in self.audio_queues:
            del self.audio_queues[room_id]
        
        logger.info(f"🛑 Room {room_id} stopped")
    
    async def process_audio(
        self,
        room_id: str,
        participant_id: str,
        audio_data: bytes,
        sample_rate: int = 48000,
        source_language: str = "en"
    ):
        """
        Queue audio for processing
        
        Args:
            room_id: Room identifier
            participant_id: Participant who sent audio
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            source_language: Source language
        """
        if room_id not in self.active_rooms:
            await self.start_room(room_id)
        
        # Convert bytes to numpy array
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            # Normalize to [-1, 1]
            audio_array = audio_array / 32768.0
            
            # Create audio chunk
            chunk = AudioChunk(
                data=audio_array,
                sample_rate=sample_rate,
                timestamp=time.time(),
                participant_id=participant_id,
                room_id=room_id,
                source_language=source_language
            )
            
            # Queue for processing
            queue = self.audio_queues.get(room_id)
            if queue:
                try:
                    queue.put_nowait(chunk)
                except asyncio.QueueFull:
                    logger.warning(f"⚠️ Audio queue full for room {room_id}, dropping chunk")
        
        except Exception as e:
            logger.error(f"❌ Error processing audio: {e}")
    
    async def _process_room_audio(self, room_id: str):
        """Background task to process audio for a room"""
        logger.info(f"🔄 Starting audio processor for room {room_id}")
        
        queue = self.audio_queues.get(room_id)
        if not queue:
            return
        
        while room_id in self.active_rooms:
            try:
                # Get audio chunk from queue
                chunk = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Get participant and their target languages
                participant = signaling_server.participants.get(chunk.participant_id)
                if not participant:
                    continue
                
                target_languages = list(participant.target_languages)
                if not target_languages:
                    continue
                
                # Process through ML pipeline
                start_time = time.time()
                
                results = await ml_pipeline.process_audio_chunk(
                    audio_chunk=chunk,
                    target_languages=target_languages,
                    voice_profile=None  # TODO: Get from participant voice profile
                )
                
                # Track performance
                latency_ms = (time.time() - start_time) * 1000
                self.processed_chunks += 1
                self.total_latency_ms += latency_ms
                
                # Send results to appropriate participants
                await self._distribute_audio(room_id, chunk.participant_id, results)
                
                if latency_ms > sfu_config.target_e2e_latency_ms:
                    logger.warning(
                        f"⚠️ High latency: {latency_ms:.0f}ms "
                        f"(target: {sfu_config.target_e2e_latency_ms}ms)"
                    )
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in audio processor: {e}")
        
        logger.info(f"🛑 Audio processor stopped for room {room_id}")
    
    async def _distribute_audio(
        self,
        room_id: str,
        sender_id: str,
        results: Dict
    ):
        """
        Distribute processed audio to participants
        
        Args:
            room_id: Room identifier
            sender_id: Participant who sent original audio
            results: Dict of language -> SynthesisResult
        """
        if room_id not in signaling_server.rooms:
            return
        
        # Get all participants except sender
        participant_ids = signaling_server.rooms[room_id]
        
        for participant_id in participant_ids:
            if participant_id == sender_id:
                continue
            
            participant = signaling_server.participants.get(participant_id)
            if not participant:
                continue
            
            # Find audio for participant's target language
            # For now, use first target language
            target_lang = list(participant.target_languages)[0] if participant.target_languages else "en"
            
            if target_lang not in results:
                continue
            
            synthesis = results[target_lang]
            
            # Send audio via WebRTC
            # In production, this would push audio to the WebRTC consumer
            # For now, send via WebSocket as notification
            try:
                await signaling_server.send_message(participant.websocket, {
                    "type": "translatedAudio",
                    "senderId": sender_id,
                    "language": target_lang,
                    "text": synthesis.text,
                    "audioLength": len(synthesis.audio),
                    "latencyMs": synthesis.latency_ms
                })
            except Exception as e:
                logger.error(f"❌ Failed to send audio to {participant_id}: {e}")
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        avg_latency = (
            self.total_latency_ms / self.processed_chunks 
            if self.processed_chunks > 0 
            else 0
        )
        
        return {
            "active_rooms": len(self.active_rooms),
            "processed_chunks": self.processed_chunks,
            "avg_latency_ms": avg_latency,
            "queue_sizes": {
                room_id: queue.qsize() 
                for room_id, queue in self.audio_queues.items()
            }
        }


# Singleton instance
room_orchestrator = RoomOrchestrator()
