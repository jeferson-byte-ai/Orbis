"""
SFU Server - FastAPI Application
High-performance WebRTC SFU with real-time ML translation
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sfu.config import sfu_config
from sfu.mediasoup_worker import mediasoup_manager
from sfu.signaling_server import signaling_server
from sfu.ml_pipeline import ml_pipeline
from sfu.room_orchestrator import room_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting SFU server...")
    
    # Initialize mediasoup workers
    await mediasoup_manager.initialize()
    
    # Initialize ML pipeline
    if sfu_config.enable_asr or sfu_config.enable_translation or sfu_config.enable_tts:
        try:
            await ml_pipeline.initialize()
        except Exception as e:
            logger.warning(f"⚠️ ML pipeline initialization failed: {e}")
            logger.warning("Continuing without ML features")
    
    logger.info("✅ SFU server ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down SFU server...")


# Create FastAPI app
app = FastAPI(
    title="Orbis SFU Server",
    version="1.0.0",
    description="High-performance WebRTC SFU with real-time ML translation",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Orbis SFU Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "websocket": "/ws/{room_id}",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mediasoup": {
            "workers": len(mediasoup_manager.workers),
            "ready": all(w.is_ready for w in mediasoup_manager.workers.values())
        },
        "ml_pipeline": {
            "enabled": sfu_config.enable_asr and sfu_config.enable_translation and sfu_config.enable_tts,
            "asr_ready": ml_pipeline.asr_service is not None and getattr(ml_pipeline.asr_service, "model_loaded", False),
            "mt_ready": ml_pipeline.mt_service is not None and ml_pipeline.mt_service.model is not None,
            "tts_ready": ml_pipeline.tts_service is not None and ml_pipeline.tts_service.tts is not None
        }
    }


@app.get("/stats")
def get_stats():
    """Get server statistics"""
    return {
        "config": {
            "max_rooms": sfu_config.max_rooms,
            "max_participants_per_room": sfu_config.max_participants_per_room,
            "target_latency_ms": sfu_config.target_e2e_latency_ms,
        },
        "signaling": signaling_server.get_stats(),
        "orchestrator": room_orchestrator.get_stats(),
        "ml_pipeline": ml_pipeline.get_stats() if ml_pipeline.asr_service else None
    }


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    user_id: str = Query(None)
):
    """
    WebSocket endpoint for WebRTC signaling
    
    Args:
        room_id: Room to join
        user_id: Optional user identifier
    """
    try:
        await signaling_server.handle_connection(
            websocket=websocket,
            room_id=room_id,
            user_id=user_id
        )
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for room {room_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@app.post("/rooms/{room_id}/audio")
async def receive_audio(
    room_id: str,
    participant_id: str = Query(...),
    audio_data: bytes = None
):
    """
    Receive audio for processing (alternative to WebRTC data channel)
    
    Args:
        room_id: Room identifier
        participant_id: Participant identifier
        audio_data: Raw audio bytes
    """
    try:
        await room_orchestrator.process_audio(
            room_id=room_id,
            participant_id=participant_id,
            audio_data=audio_data
        )
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error receiving audio: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/rooms/{room_id}/start")
async def start_room(room_id: str):
    """Start a room"""
    try:
        await room_orchestrator.start_room(room_id)
        return {"status": "started", "room_id": room_id}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/rooms/{room_id}/stop")
async def stop_room(room_id: str):
    """Stop a room"""
    try:
        await room_orchestrator.stop_room(room_id)
        return {"status": "stopped", "room_id": room_id}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/config")
def get_config():
    """Get SFU configuration"""
    return {
        "listen_port": sfu_config.listen_port,
        "rtc_port_range": f"{sfu_config.rtc_min_port}-{sfu_config.rtc_max_port}",
        "audio_codec": sfu_config.audio_codec,
        "video_codec": sfu_config.video_codec,
        "max_rooms": sfu_config.max_rooms,
        "max_participants_per_room": sfu_config.max_participants_per_room,
        "target_latencies": {
            "e2e_ms": sfu_config.target_e2e_latency_ms,
            "network_ms": sfu_config.target_network_latency_ms,
            "ml_ms": sfu_config.target_ml_latency_ms
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "sfu.server:app",
        host=sfu_config.listen_ip,
        port=sfu_config.listen_port,
        reload=True,
        log_level="info"
    )
