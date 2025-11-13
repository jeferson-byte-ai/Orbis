"""
Mediasoup Worker Manager
High-performance SFU using mediasoup for WebRTC
"""
import asyncio
import logging
import json
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MediasoupWorker:
    """Represents a mediasoup worker process"""
    worker_id: str
    pid: Optional[int] = None
    routers: Dict[str, 'Router'] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_ready: bool = False
    
    @property
    def router_count(self) -> int:
        return len(self.routers)


@dataclass
class Router:
    """Represents a mediasoup router"""
    router_id: str
    worker_id: str
    room_id: str
    transports: Dict[str, 'Transport'] = field(default_factory=dict)
    producers: Dict[str, 'Producer'] = field(default_factory=dict)
    consumers: Dict[str, 'Consumer'] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Transport:
    """WebRTC transport"""
    transport_id: str
    router_id: str
    participant_id: str
    direction: str  # 'send' or 'recv'
    dtls_parameters: Optional[Dict] = None
    ice_parameters: Optional[Dict] = None
    ice_candidates: List[Dict] = field(default_factory=list)
    state: str = "new"  # new, connecting, connected, failed, closed


@dataclass
class Producer:
    """Media producer (sender)"""
    producer_id: str
    transport_id: str
    participant_id: str
    kind: str  # 'audio' or 'video'
    rtp_parameters: Optional[Dict] = None
    paused: bool = False


@dataclass
class Consumer:
    """Media consumer (receiver)"""
    consumer_id: str
    transport_id: str
    producer_id: str
    participant_id: str
    kind: str  # 'audio' or 'video'
    rtp_parameters: Optional[Dict] = None
    paused: bool = False


class MediasoupWorkerManager:
    """
    Manages mediasoup workers for high-performance WebRTC SFU
    
    In production, this would use the actual mediasoup Node.js library.
    This implementation provides the Python interface and management layer.
    """
    
    def __init__(self, num_workers: int = 4):
        """
        Initialize worker manager
        
        Args:
            num_workers: Number of worker processes (typically = CPU cores)
        """
        self.num_workers = num_workers
        self.workers: Dict[str, MediasoupWorker] = {}
        self.current_worker_index = 0
        self._lock = asyncio.Lock()
        
        logger.info(f"🎬 Initializing Mediasoup with {num_workers} workers")
    
    async def initialize(self):
        """Initialize all workers"""
        try:
            for i in range(self.num_workers):
                worker_id = f"worker-{i}"
                worker = MediasoupWorker(worker_id=worker_id)
                
                # In production, launch actual mediasoup worker process here
                worker.is_ready = True
                self.workers[worker_id] = worker
                
                logger.info(f"✅ Worker {worker_id} initialized")
            
            logger.info(f"🎯 All {self.num_workers} workers ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize workers: {e}")
            raise
    
    def get_least_loaded_worker(self) -> Optional[MediasoupWorker]:
        """Get worker with least load (round-robin)"""
        if not self.workers:
            return None
        
        # Simple round-robin for now
        worker_ids = list(self.workers.keys())
        worker_id = worker_ids[self.current_worker_index % len(worker_ids)]
        self.current_worker_index += 1
        
        return self.workers[worker_id]
    
    async def create_router(self, room_id: str) -> Optional[Router]:
        """
        Create a router for a room
        
        Args:
            room_id: Unique room identifier
        
        Returns:
            Router instance
        """
        try:
            worker = self.get_least_loaded_worker()
            if not worker:
                logger.error("No workers available")
                return None
            
            router_id = f"router-{room_id}"
            router = Router(
                router_id=router_id,
                worker_id=worker.worker_id,
                room_id=room_id
            )
            
            worker.routers[router_id] = router
            
            logger.info(f"✅ Router {router_id} created for room {room_id} on {worker.worker_id}")
            return router
            
        except Exception as e:
            logger.error(f"❌ Failed to create router: {e}")
            return None
    
    async def create_webrtc_transport(
        self,
        router: Router,
        participant_id: str,
        direction: str
    ) -> Optional[Transport]:
        """
        Create WebRTC transport for participant
        
        Args:
            router: Router to create transport on
            participant_id: Participant identifier
            direction: 'send' or 'recv'
        
        Returns:
            Transport instance
        """
        try:
            transport_id = f"transport-{participant_id}-{direction}"
            
            # Mock ICE/DTLS parameters (in production, get from mediasoup)
            ice_parameters = {
                "iceLite": True,
                "usernameFragment": f"user-{participant_id[:8]}",
                "password": f"pass-{participant_id[:8]}"
            }
            
            ice_candidates = [
                {
                    "foundation": "udpcandidate",
                    "priority": 1076302079,
                    "ip": "127.0.0.1",  # In production, use actual IP
                    "port": 40000,
                    "type": "host",
                    "protocol": "udp"
                }
            ]
            
            dtls_parameters = {
                "role": "auto",
                "fingerprints": [{
                    "algorithm": "sha-256",
                    "value": "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00"
                }]
            }
            
            transport = Transport(
                transport_id=transport_id,
                router_id=router.router_id,
                participant_id=participant_id,
                direction=direction,
                ice_parameters=ice_parameters,
                ice_candidates=ice_candidates,
                dtls_parameters=dtls_parameters
            )
            
            router.transports[transport_id] = transport
            
            logger.info(f"✅ Transport {transport_id} created for {participant_id} ({direction})")
            return transport
            
        except Exception as e:
            logger.error(f"❌ Failed to create transport: {e}")
            return None
    
    async def create_producer(
        self,
        transport: Transport,
        kind: str,
        rtp_parameters: Dict
    ) -> Optional[Producer]:
        """
        Create producer on transport
        
        Args:
            transport: Transport to create producer on
            kind: 'audio' or 'video'
            rtp_parameters: RTP parameters from client
        
        Returns:
            Producer instance
        """
        try:
            producer_id = f"producer-{transport.participant_id}-{kind}"
            
            producer = Producer(
                producer_id=producer_id,
                transport_id=transport.transport_id,
                participant_id=transport.participant_id,
                kind=kind,
                rtp_parameters=rtp_parameters
            )
            
            # Find router and add producer
            for worker in self.workers.values():
                for router in worker.routers.values():
                    if transport.transport_id in router.transports:
                        router.producers[producer_id] = producer
                        break
            
            logger.info(f"✅ Producer {producer_id} created ({kind})")
            return producer
            
        except Exception as e:
            logger.error(f"❌ Failed to create producer: {e}")
            return None
    
    async def create_consumer(
        self,
        transport: Transport,
        producer: Producer,
        rtp_capabilities: Dict
    ) -> Optional[Consumer]:
        """
        Create consumer for producer
        
        Args:
            transport: Transport to create consumer on
            producer: Producer to consume
            rtp_capabilities: Client RTP capabilities
        
        Returns:
            Consumer instance
        """
        try:
            consumer_id = f"consumer-{transport.participant_id}-{producer.producer_id}"
            
            consumer = Consumer(
                consumer_id=consumer_id,
                transport_id=transport.transport_id,
                producer_id=producer.producer_id,
                participant_id=transport.participant_id,
                kind=producer.kind,
                rtp_parameters=producer.rtp_parameters
            )
            
            # Find router and add consumer
            for worker in self.workers.values():
                for router in worker.routers.values():
                    if transport.transport_id in router.transports:
                        router.consumers[consumer_id] = consumer
                        break
            
            logger.info(f"✅ Consumer {consumer_id} created for producer {producer.producer_id}")
            return consumer
            
        except Exception as e:
            logger.error(f"❌ Failed to create consumer: {e}")
            return None
    
    async def close_producer(self, producer_id: str):
        """Close producer"""
        for worker in self.workers.values():
            for router in worker.routers.values():
                if producer_id in router.producers:
                    del router.producers[producer_id]
                    logger.info(f"🔒 Producer {producer_id} closed")
                    return
    
    async def close_consumer(self, consumer_id: str):
        """Close consumer"""
        for worker in self.workers.values():
            for router in worker.routers.values():
                if consumer_id in router.consumers:
                    del router.consumers[consumer_id]
                    logger.info(f"🔒 Consumer {consumer_id} closed")
                    return
    
    async def close_transport(self, transport_id: str):
        """Close transport"""
        for worker in self.workers.values():
            for router in worker.routers.values():
                if transport_id in router.transports:
                    del router.transports[transport_id]
                    logger.info(f"🔒 Transport {transport_id} closed")
                    return
    
    async def close_router(self, router_id: str):
        """Close router and all associated resources"""
        for worker in self.workers.values():
            if router_id in worker.routers:
                del worker.routers[router_id]
                logger.info(f"🔒 Router {router_id} closed")
                return
    
    def get_stats(self) -> Dict:
        """Get SFU statistics"""
        total_routers = sum(len(w.routers) for w in self.workers.values())
        total_transports = sum(
            len(r.transports) 
            for w in self.workers.values() 
            for r in w.routers.values()
        )
        total_producers = sum(
            len(r.producers) 
            for w in self.workers.values() 
            for r in w.routers.values()
        )
        total_consumers = sum(
            len(r.consumers) 
            for w in self.workers.values() 
            for r in w.routers.values()
        )
        
        return {
            "workers": len(self.workers),
            "routers": total_routers,
            "transports": total_transports,
            "producers": total_producers,
            "consumers": total_consumers,
            "worker_details": {
                worker_id: {
                    "routers": worker.router_count,
                    "ready": worker.is_ready
                }
                for worker_id, worker in self.workers.items()
            }
        }


# Singleton instance
mediasoup_manager = MediasoupWorkerManager(num_workers=4)
