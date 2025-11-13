"""
Lazy Loading Service
Loads ML models on-demand to reduce startup time and memory usage
Automatically unloads models after idle period to save RAM
"""
import asyncio
import logging
import time
import psutil
import torch
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of ML models"""
    WHISPER = "whisper"  # ASR (Speech-to-Text)
    NLLB = "nllb"  # Translation
    COQUI = "coqui"  # TTS (Text-to-Speech)


class ModelStatus(Enum):
    """Model loading status"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"


class ModelInfo:
    """Information about a loaded model"""
    
    def __init__(self, model_type: ModelType, service: Any):
        self.model_type = model_type
        self.service = service
        self.status = ModelStatus.UNLOADED
        self.loaded_at: Optional[datetime] = None
        self.last_used: Optional[datetime] = None
        self.use_count: int = 0
        self.load_time: float = 0.0
        self.memory_usage_mb: float = 0.0
        self.error_message: Optional[str] = None
    
    def mark_used(self):
        """Mark model as recently used"""
        self.last_used = datetime.now()
        self.use_count += 1
    
    def is_idle(self, idle_timeout_seconds: int) -> bool:
        """Check if model has been idle for too long"""
        if not self.last_used or self.status != ModelStatus.LOADED:
            return False
        
        idle_time = datetime.now() - self.last_used
        return idle_time.total_seconds() > idle_timeout_seconds
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "model_type": self.model_type.value,
            "status": self.status.value,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
            "load_time_seconds": round(self.load_time, 2),
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "idle_seconds": (datetime.now() - self.last_used).total_seconds() if self.last_used else None,
            "error": self.error_message
        }


class LazyLoadService:
    """
    Lazy loading service for ML models
    - Loads models on first use
    - Tracks usage and memory
    - Automatically unloads idle models
    """
    
    def __init__(
        self,
        idle_timeout_seconds: int = 3600,  # 1 hour
        enable_auto_unload: bool = True,
        check_interval_seconds: int = 300  # Check every 5 minutes
    ):
        self.idle_timeout_seconds = idle_timeout_seconds
        self.enable_auto_unload = enable_auto_unload
        self.check_interval_seconds = check_interval_seconds
        
        self.models: Dict[ModelType, ModelInfo] = {}
        self._unload_task: Optional[asyncio.Task] = None
        self._loading_locks: Dict[ModelType, asyncio.Lock] = {
            ModelType.WHISPER: asyncio.Lock(),
            ModelType.NLLB: asyncio.Lock(),
            ModelType.COQUI: asyncio.Lock()
        }
        
        logger.info(
            f"🔄 Lazy Loading Service initialized "
            f"(idle_timeout={idle_timeout_seconds}s, auto_unload={enable_auto_unload})"
        )
    
    def register_model(self, model_type: ModelType, service: Any):
        """Register a model service for lazy loading"""
        self.models[model_type] = ModelInfo(model_type, service)
        logger.info(f"📝 Registered {model_type.value} for lazy loading")
    
    async def load_model(self, model_type: ModelType, force: bool = False) -> bool:
        """
        Load a model if not already loaded
        
        Args:
            model_type: Type of model to load
            force: Force reload even if already loaded
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if model_type not in self.models:
            logger.error(f"❌ Model type {model_type.value} not registered")
            return False
        
        model_info = self.models[model_type]
        
        # If already loaded and not forcing reload
        if model_info.status == ModelStatus.LOADED and not force:
            model_info.mark_used()
            logger.debug(f"✅ {model_type.value} already loaded (uses: {model_info.use_count})")
            return True
        
        # If currently loading, wait for it
        if model_info.status == ModelStatus.LOADING:
            logger.info(f"⏳ {model_type.value} is already loading, waiting...")
            while model_info.status == ModelStatus.LOADING:
                await asyncio.sleep(0.5)
            return model_info.status == ModelStatus.LOADED
        
        # Acquire lock to prevent multiple simultaneous loads
        async with self._loading_locks[model_type]:
            # Double-check status after acquiring lock
            if model_info.status == ModelStatus.LOADED and not force:
                model_info.mark_used()
                return True
            
            try:
                model_info.status = ModelStatus.LOADING
                model_info.error_message = None
                
                logger.info(f"⏳ Loading {model_type.value} model...")
                
                # Measure memory before loading
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                
                start_time = time.time()
                
                # Load model in executor to not block event loop
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, model_info.service.load)
                
                load_time = time.time() - start_time
                
                # Measure memory after loading
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                mem_used = mem_after - mem_before
                
                # Update model info
                model_info.status = ModelStatus.LOADED
                model_info.loaded_at = datetime.now()
                model_info.last_used = datetime.now()
                model_info.use_count = 1
                model_info.load_time = load_time
                model_info.memory_usage_mb = mem_used
                
                logger.info(
                    f"✅ {model_type.value} loaded successfully "
                    f"(time: {load_time:.1f}s, RAM: +{mem_used:.0f}MB)"
                )
                
                return True
                
            except Exception as e:
                model_info.status = ModelStatus.ERROR
                model_info.error_message = str(e)
                logger.error(f"❌ Failed to load {model_type.value}: {e}")
                return False
    
    async def unload_model(self, model_type: ModelType) -> bool:
        """
        Unload a model to free memory
        
        Args:
            model_type: Type of model to unload
        
        Returns:
            True if unloaded successfully
        """
        if model_type not in self.models:
            logger.error(f"❌ Model type {model_type.value} not registered")
            return False
        
        model_info = self.models[model_type]
        
        if model_info.status != ModelStatus.LOADED:
            logger.debug(f"ℹ️ {model_type.value} is not loaded, nothing to unload")
            return True
        
        try:
            logger.info(f"🗑️ Unloading {model_type.value} model...")
            
            # Measure memory before unloading
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Clear model references
            service = model_info.service
            
            if model_type == ModelType.WHISPER:
                service.model = None
                service.model_loaded = False
            elif model_type == ModelType.NLLB:
                service.model = None
                service.tokenizer = None
            elif model_type == ModelType.COQUI:
                service.tts = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Measure memory after unloading
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_freed = mem_before - mem_after
            
            # Update model info
            model_info.status = ModelStatus.UNLOADED
            model_info.loaded_at = None
            
            logger.info(
                f"✅ {model_type.value} unloaded (RAM freed: ~{mem_freed:.0f}MB, "
                f"total uses: {model_info.use_count})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unload {model_type.value}: {e}")
            return False
    
    async def ensure_loaded(self, model_type: ModelType) -> bool:
        """
        Ensure a model is loaded before use
        Loads it if necessary and marks as used
        
        Args:
            model_type: Type of model needed
        
        Returns:
            True if model is ready to use
        """
        success = await self.load_model(model_type)
        if success and model_type in self.models:
            self.models[model_type].mark_used()
        return success
    
    async def start_auto_unload_task(self):
        """Start background task to automatically unload idle models"""
        if not self.enable_auto_unload:
            logger.info("ℹ️ Auto-unload disabled")
            return
        
        if self._unload_task and not self._unload_task.done():
            logger.warning("⚠️ Auto-unload task already running")
            return
        
        self._unload_task = asyncio.create_task(self._auto_unload_loop())
        logger.info(
            f"🔄 Started auto-unload task "
            f"(check every {self.check_interval_seconds}s, timeout: {self.idle_timeout_seconds}s)"
        )
    
    async def stop_auto_unload_task(self):
        """Stop background auto-unload task"""
        if self._unload_task and not self._unload_task.done():
            self._unload_task.cancel()
            try:
                await self._unload_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Stopped auto-unload task")
    
    async def _auto_unload_loop(self):
        """Background loop to check and unload idle models"""
        while True:
            try:
                await asyncio.sleep(self.check_interval_seconds)
                
                for model_type, model_info in self.models.items():
                    if model_info.is_idle(self.idle_timeout_seconds):
                        idle_time = (datetime.now() - model_info.last_used).total_seconds()
                        logger.info(
                            f"💤 {model_type.value} has been idle for {idle_time:.0f}s, unloading..."
                        )
                        await self.unload_model(model_type)
                
            except asyncio.CancelledError:
                logger.info("🛑 Auto-unload loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in auto-unload loop: {e}")
    
    def get_status(self) -> Dict:
        """Get status of all models"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "lazy_loading_enabled": True,
            "auto_unload_enabled": self.enable_auto_unload,
            "idle_timeout_seconds": self.idle_timeout_seconds,
            "check_interval_seconds": self.check_interval_seconds,
            "system_memory": {
                "process_rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "process_vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "system_available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
                "system_total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
                "system_percent": psutil.virtual_memory().percent
            },
            "models": {
                model_type.value: model_info.to_dict()
                for model_type, model_info in self.models.items()
            }
        }
    
    async def unload_all(self):
        """Unload all loaded models"""
        logger.info("🗑️ Unloading all models...")
        for model_type in self.models.keys():
            await self.unload_model(model_type)
        logger.info("✅ All models unloaded")


# Global singleton instance
lazy_loader = LazyLoadService(
    idle_timeout_seconds=3600,  # 1 hour
    enable_auto_unload=True,
    check_interval_seconds=300  # Check every 5 minutes
)
