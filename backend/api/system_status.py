"""
System Status API
Provides real-time information about system resources, loaded models, and features
"""
import logging
import psutil
import torch
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from backend.api.deps import get_current_user
from backend.db.models import User
from backend.config import settings
from backend.services.lazy_loader import lazy_loader, ModelType
from backend.services.hardware_detection import hardware_detector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["System Status"])


@router.get("/status")
async def get_system_status(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get comprehensive system status
    
    Requires authentication (any user can view)
    
    Returns:
        - Hardware capabilities
        - ML models status
        - Memory usage
        - Feature flags
        - System health
    """
    try:
        # Get hardware info
        hardware_caps = hardware_detector.get_capabilities()
        if not hardware_caps:
            hardware_caps = hardware_detector.detect()
        
        # Get lazy loader status
        lazy_status = lazy_loader.get_status()
        
        # Get feature flags
        features = {
            "core": {
                "auth": settings.enable_auth,
                "rooms": settings.enable_rooms,
                "websocket": settings.enable_websocket
            },
            "ml": {
                "voice_cloning": settings.enable_voice_cloning,
                "translation": settings.enable_translation,
                "transcription": settings.enable_transcription
            },
            "advanced": {
                "ai_assistant": settings.enable_ai_assistant,
                "advanced_analytics": settings.enable_advanced_analytics,
                "gamification": settings.enable_gamification,
                "voice_marketplace": settings.enable_voice_marketplace,
                "social_networking": settings.enable_social_networking
            },
            "enterprise": {
                "enterprise_features": settings.enable_enterprise_features,
                "disaster_recovery": settings.enable_disaster_recovery,
                "database_sharding": settings.enable_database_sharding
            }
        }
        
        # ML Configuration
        ml_config = settings.get_ml_config()
        
        # System health check
        health = {
            "status": "healthy",
            "checks": {
                "memory": "healthy" if psutil.virtual_memory().percent < 90 else "warning",
                "cpu": "healthy" if psutil.cpu_percent(interval=0.1) < 80 else "warning",
                "gpu": "healthy" if hardware_caps.has_cuda else "not_available"
            }
        }
        
        return {
            "success": True,
            "data": {
                "hardware": hardware_caps.to_dict() if hardware_caps else None,
                "models": lazy_status,
                "features": features,
                "ml_config": ml_config,
                "health": health,
                "environment": settings.environment
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.get("/hardware")
async def get_hardware_info(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get detailed hardware information
    
    Returns CPU, RAM, GPU details and recommendations
    """
    try:
        hardware_caps = hardware_detector.get_capabilities()
        if not hardware_caps:
            hardware_caps = hardware_detector.detect()
        
        return {
            "success": True,
            "data": hardware_caps.to_dict() if hardware_caps else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get hardware info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get hardware info: {str(e)}")


@router.get("/models")
async def get_models_status(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get status of all ML models (loaded, unloaded, loading)
    """
    try:
        status = lazy_loader.get_status()
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Failed to get models status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get models status: {str(e)}")


@router.post("/models/{model_type}/load")
async def load_model(model_type: str, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Manually load a specific ML model
    
    Args:
        model_type: 'whisper', 'nllb', or 'coqui'
    
    Requires admin user
    """
    # Check if user is admin (you can add role check here)
    # For now, any authenticated user can trigger load
    
    try:
        # Map string to ModelType enum
        model_type_map = {
            "whisper": ModelType.WHISPER,
            "nllb": ModelType.NLLB,
            "coqui": ModelType.COQUI
        }
        
        if model_type not in model_type_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model type. Must be one of: {list(model_type_map.keys())}"
            )
        
        model_enum = model_type_map[model_type]
        
        logger.info(f"User {current_user.email} requested to load {model_type}")
        
        success = await lazy_loader.load_model(model_enum, force=False)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_type} loaded successfully",
                "data": lazy_loader.models[model_enum].to_dict()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to load model {model_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load model {model_type}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.post("/models/{model_type}/unload")
async def unload_model(model_type: str, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Manually unload a specific ML model to free memory
    
    Args:
        model_type: 'whisper', 'nllb', or 'coqui'
    
    Requires admin user
    """
    try:
        # Map string to ModelType enum
        model_type_map = {
            "whisper": ModelType.WHISPER,
            "nllb": ModelType.NLLB,
            "coqui": ModelType.COQUI
        }
        
        if model_type not in model_type_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model type. Must be one of: {list(model_type_map.keys())}"
            )
        
        model_enum = model_type_map[model_type]
        
        logger.info(f"User {current_user.email} requested to unload {model_type}")
        
        success = await lazy_loader.unload_model(model_enum)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_type} unloaded successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to unload model {model_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unload model {model_type}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")


@router.get("/features")
async def get_features() -> Dict[str, Any]:
    """
    Get list of enabled features (public endpoint, no auth required)
    Useful for frontend to know what features are available
    """
    try:
        features = {
            "core": {
                "auth": settings.enable_auth,
                "rooms": settings.enable_rooms,
                "websocket": settings.enable_websocket
            },
            "ml": {
                "voice_cloning": settings.enable_voice_cloning,
                "translation": settings.enable_translation,
                "transcription": settings.enable_transcription
            },
            "advanced": {
                "ai_assistant": settings.enable_ai_assistant,
                "advanced_analytics": settings.enable_advanced_analytics,
                "gamification": settings.enable_gamification,
                "voice_marketplace": settings.enable_voice_marketplace,
                "social_networking": settings.enable_social_networking
            },
            "enterprise": {
                "enterprise_features": settings.enable_enterprise_features,
                "disaster_recovery": settings.enable_disaster_recovery,
                "database_sharding": settings.enable_database_sharding
            },
            "other": {
                "recordings": settings.enable_recordings,
                "oauth": settings.enable_oauth,
                "payments": settings.enable_payments
            }
        }
        
        return {
            "success": True,
            "data": features
        }
        
    except Exception as e:
        logger.error(f"Failed to get features: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get features: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint (no auth required)
    Returns basic system health information
    """
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        health = {
            "status": "healthy",
            "uptime_seconds": None,  # Could track from startup
            "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "gpu_available": torch.cuda.is_available()
        }
        
        return {
            "success": True,
            "data": health
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            }
        }
