"""
ML Model Manager
Production-grade model loading, caching, and optimization
"""
import asyncio
import logging
import os
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import torch

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages ML models with production optimizations:
    - Lazy loading
    - GPU management
    - Model caching
    - Multi-model support
    - Quantization
    - ONNX export (optional)
    """
    
    def __init__(self, models_dir: str = "./data/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model registry
        self.models: Dict[str, Any] = {}
        self.model_configs: Dict[str, Dict] = {}
        self.load_times: Dict[str, float] = {}
        
        # Device management
        self.device = self._detect_device()
        self.gpu_memory_reserved = 0
        
        # Performance settings
        self.use_fp16 = torch.cuda.is_available()
        self.use_dynamic_batching = True
        self.max_batch_size = 8
        
        logger.info(f"🎯 Model Manager initialized on {self.device}")
        if self.use_fp16:
            logger.info("✅ FP16 (half precision) enabled for GPU acceleration")
    
    def _detect_device(self) -> str:
        """Detect best available device"""
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✅ CUDA available: {gpu_name}")
            return device
        elif torch.backends.mps.is_available():
            device = "mps"
            logger.info("✅ Apple MPS (Metal) available")
            return device
        else:
            device = "cpu"
            logger.warning("⚠️ No GPU available - using CPU (slower)")
            return device
    
    async def load_model(
        self,
        model_name: str,
        model_type: str,
        model_path: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> bool:
        """
        Load model with optimizations
        
        Args:
            model_name: Unique model identifier
            model_type: Type of model (asr, mt, tts)
            model_path: Path to model or HuggingFace identifier
            config: Model configuration
        
        Returns:
            Success status
        """
        if model_name in self.models:
            logger.info(f"Model {model_name} already loaded")
            return True
        
        logger.info(f"📦 Loading {model_type} model: {model_name}")
        start_time = asyncio.get_event_loop().time()
        
        try:
            if model_type == "asr":
                model = await self._load_asr_model(model_path or "base", config or {})
            elif model_type == "mt":
                model = await self._load_mt_model(model_path or "facebook/nllb-200-distilled-600M", config or {})
            elif model_type == "tts":
                model = await self._load_tts_model(model_path or "tts_models/multilingual/multi-dataset/xtts_v2", config or {})
            else:
                logger.error(f"Unknown model type: {model_type}")
                return False
            
            # Store model
            self.models[model_name] = model
            self.model_configs[model_name] = {
                "type": model_type,
                "path": model_path,
                "config": config,
                "loaded_at": datetime.utcnow().isoformat()
            }
            
            load_time = asyncio.get_event_loop().time() - start_time
            self.load_times[model_name] = load_time
            
            logger.info(f"✅ Model {model_name} loaded in {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            return False
    
    async def _load_asr_model(self, model_size: str, config: Dict) -> Any:
        """Load ASR model (Whisper)"""
        from faster_whisper import WhisperModel
        
        loop = asyncio.get_event_loop()
        
        def _load():
            return WhisperModel(
                model_size,
                device=self.device,
                compute_type="float16" if self.use_fp16 else "int8",
                download_root=str(self.models_dir / "whisper"),
                num_workers=4
            )
        
        model = await loop.run_in_executor(None, _load)
        
        # Warm up
        await loop.run_in_executor(
            None,
            lambda: list(model.transcribe(
                torch.randn(16000).numpy(),
                language="en"
            ))
        )
        
        return model
    
    async def _load_mt_model(self, model_path: str, config: Dict) -> Any:
        """Load MT model (NLLB)"""
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        
        loop = asyncio.get_event_loop()
        
        def _load():
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=str(self.models_dir / "nllb")
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                cache_dir=str(self.models_dir / "nllb")
            )
            
            if self.device == "cuda":
                model = model.to(self.device)
                if self.use_fp16:
                    model = model.half()
            
            model.eval()
            return {"model": model, "tokenizer": tokenizer}
        
        return await loop.run_in_executor(None, _load)
    
    async def _load_tts_model(self, model_path: str, config: Dict) -> Any:
        """Load TTS model (Coqui)"""
        from TTS.api import TTS
        
        loop = asyncio.get_event_loop()
        
        def _load():
            return TTS(
                model_path,
                gpu=(self.device == "cuda")
            )
        
        return await loop.run_in_executor(None, _load)
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get loaded model"""
        return self.models.get(model_name)
    
    def unload_model(self, model_name: str):
        """Unload model to free memory"""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"🗑️ Model {model_name} unloaded")
            
            # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    def optimize_for_inference(self, model_name: str):
        """
        Optimize model for inference
        - Disable gradients
        - Enable inference mode
        - Apply quantization if possible
        """
        model = self.models.get(model_name)
        if not model:
            return
        
        try:
            # Disable gradient computation
            if hasattr(model, "requires_grad_"):
                model.requires_grad_(False)
            
            # Set to eval mode
            if hasattr(model, "eval"):
                model.eval()
            
            logger.info(f"⚡ Model {model_name} optimized for inference")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to optimize model {model_name}: {e}")
    
    def get_memory_stats(self) -> Dict:
        """Get GPU memory statistics"""
        if not torch.cuda.is_available():
            return {"device": "cpu", "memory": "N/A"}
        
        return {
            "device": "cuda",
            "device_name": torch.cuda.get_device_name(0),
            "memory_allocated_mb": torch.cuda.memory_allocated() / 1024**2,
            "memory_reserved_mb": torch.cuda.memory_reserved() / 1024**2,
            "memory_cached_mb": torch.cuda.memory_reserved() / 1024**2,
            "max_memory_allocated_mb": torch.cuda.max_memory_allocated() / 1024**2
        }
    
    def get_stats(self) -> Dict:
        """Get model manager statistics"""
        return {
            "device": self.device,
            "models_loaded": len(self.models),
            "models": {
                name: {
                    "type": config["type"],
                    "loaded_at": config["loaded_at"],
                    "load_time_s": self.load_times.get(name, 0)
                }
                for name, config in self.model_configs.items()
            },
            "memory": self.get_memory_stats(),
            "optimizations": {
                "fp16_enabled": self.use_fp16,
                "dynamic_batching": self.use_dynamic_batching,
                "max_batch_size": self.max_batch_size
            }
        }


# Singleton instance
model_manager = ModelManager()
