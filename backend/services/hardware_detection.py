"""
Hardware Detection Service
Automatically detects system capabilities and chooses optimal ML models
"""
import logging
import psutil
import torch
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HardwareProfile(Enum):
    """Hardware capability profiles"""
    LOW = "low"  # <4GB RAM, no GPU
    MEDIUM = "medium"  # 4-8GB RAM, or GPU with <4GB VRAM
    HIGH = "high"  # 8-16GB RAM, or GPU with 4-8GB VRAM
    ULTRA = "ultra"  # 16GB+ RAM, or GPU with 8GB+ VRAM


@dataclass
class HardwareCapabilities:
    """System hardware capabilities"""
    # CPU
    cpu_count: int
    cpu_freq_mhz: float
    cpu_usage_percent: float
    
    # Memory
    ram_total_gb: float
    ram_available_gb: float
    ram_usage_percent: float
    
    # GPU
    has_cuda: bool
    cuda_available: bool
    gpu_count: int
    gpu_name: Optional[str]
    gpu_memory_total_gb: Optional[float]
    gpu_memory_available_gb: Optional[float]
    
    # Profile
    hardware_profile: HardwareProfile
    
    # Recommendations
    recommended_whisper_model: str
    recommended_nllb_model: str
    recommended_device: str
    recommended_compute_type: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "cpu": {
                "count": self.cpu_count,
                "freq_mhz": round(self.cpu_freq_mhz, 2),
                "usage_percent": round(self.cpu_usage_percent, 2)
            },
            "memory": {
                "total_gb": round(self.ram_total_gb, 2),
                "available_gb": round(self.ram_available_gb, 2),
                "usage_percent": round(self.ram_usage_percent, 2)
            },
            "gpu": {
                "has_cuda": self.has_cuda,
                "cuda_available": self.cuda_available,
                "count": self.gpu_count,
                "name": self.gpu_name,
                "memory_total_gb": round(self.gpu_memory_total_gb, 2) if self.gpu_memory_total_gb else None,
                "memory_available_gb": round(self.gpu_memory_available_gb, 2) if self.gpu_memory_available_gb else None
            },
            "profile": self.hardware_profile.value,
            "recommendations": {
                "whisper_model": self.recommended_whisper_model,
                "nllb_model": self.recommended_nllb_model,
                "device": self.recommended_device,
                "compute_type": self.recommended_compute_type
            }
        }


class HardwareDetectionService:
    """
    Detects system hardware and recommends optimal ML model configurations
    """
    
    def __init__(self):
        self._capabilities: Optional[HardwareCapabilities] = None
        logger.info("🔍 Hardware Detection Service initialized")
    
    def detect(self) -> HardwareCapabilities:
        """
        Detect hardware capabilities and recommend configurations
        
        Returns:
            HardwareCapabilities object with system info and recommendations
        """
        logger.info("🔍 Detecting hardware capabilities...")
        
        # CPU Information
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 0.0
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Memory Information
        memory = psutil.virtual_memory()
        ram_total_gb = memory.total / (1024 ** 3)
        ram_available_gb = memory.available / (1024 ** 3)
        ram_usage_percent = memory.percent
        
        # GPU Information
        has_cuda = torch.cuda.is_available()
        cuda_available = has_cuda
        gpu_count = torch.cuda.device_count() if has_cuda else 0
        gpu_name = None
        gpu_memory_total_gb = None
        gpu_memory_available_gb = None
        
        if has_cuda and gpu_count > 0:
            try:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory_total = torch.cuda.get_device_properties(0).total_memory
                gpu_memory_total_gb = gpu_memory_total / (1024 ** 3)
                
                # Try to get available memory (requires actual GPU query)
                torch.cuda.empty_cache()
                gpu_memory_available = torch.cuda.mem_get_info(0)[0]
                gpu_memory_available_gb = gpu_memory_available / (1024 ** 3)
            except Exception as e:
                logger.warning(f"⚠️ Could not get GPU details: {e}")
        
        # Determine hardware profile
        hardware_profile = self._determine_profile(
            ram_total_gb, 
            has_cuda, 
            gpu_memory_total_gb
        )
        
        # Get model recommendations based on profile
        whisper_model, nllb_model, device, compute_type = self._get_recommendations(
            hardware_profile,
            ram_available_gb,
            has_cuda,
            gpu_memory_available_gb
        )
        
        self._capabilities = HardwareCapabilities(
            cpu_count=cpu_count,
            cpu_freq_mhz=cpu_freq_mhz,
            cpu_usage_percent=cpu_usage,
            ram_total_gb=ram_total_gb,
            ram_available_gb=ram_available_gb,
            ram_usage_percent=ram_usage_percent,
            has_cuda=has_cuda,
            cuda_available=cuda_available,
            gpu_count=gpu_count,
            gpu_name=gpu_name,
            gpu_memory_total_gb=gpu_memory_total_gb,
            gpu_memory_available_gb=gpu_memory_available_gb,
            hardware_profile=hardware_profile,
            recommended_whisper_model=whisper_model,
            recommended_nllb_model=nllb_model,
            recommended_device=device,
            recommended_compute_type=compute_type
        )
        
        self._log_detection_results()
        
        return self._capabilities
    
    def _determine_profile(
        self, 
        ram_gb: float, 
        has_gpu: bool, 
        gpu_vram_gb: Optional[float]
    ) -> HardwareProfile:
        """Determine hardware profile based on system specs"""
        
        # GPU-based profiles (GPU is more important for ML)
        if has_gpu and gpu_vram_gb:
            if gpu_vram_gb >= 8:
                return HardwareProfile.ULTRA
            elif gpu_vram_gb >= 4:
                return HardwareProfile.HIGH
            else:
                return HardwareProfile.MEDIUM
        
        # CPU-only profiles (based on RAM)
        if ram_gb >= 16:
            return HardwareProfile.HIGH
        elif ram_gb >= 8:
            return HardwareProfile.MEDIUM
        elif ram_gb >= 4:
            return HardwareProfile.LOW
        else:
            return HardwareProfile.LOW
    
    def _get_recommendations(
        self,
        profile: HardwareProfile,
        ram_available_gb: float,
        has_gpu: bool,
        gpu_vram_available_gb: Optional[float]
    ) -> Tuple[str, str, str, str]:
        """
        Get model recommendations based on hardware profile
        
        Returns:
            (whisper_model, nllb_model, device, compute_type)
        """
        
        # LOW profile: Minimal models, CPU only
        if profile == HardwareProfile.LOW:
            return (
                "base",  # Whisper base (~75MB)
                "facebook/nllb-200-distilled-600M",  # Distilled NLLB (~600MB)
                "cpu",
                "int8"  # Quantized for CPU
            )
        
        # MEDIUM profile: Balanced models
        elif profile == HardwareProfile.MEDIUM:
            if has_gpu:
                return (
                    "small",  # Whisper small (~250MB)
                    "facebook/nllb-200-distilled-600M",
                    "cuda",
                    "float16"
                )
            else:
                return (
                    "small",
                    "facebook/nllb-200-distilled-600M",
                    "cpu",
                    "int8"
                )
        
        # HIGH profile: High-quality models
        elif profile == HardwareProfile.HIGH:
            if has_gpu and gpu_vram_available_gb and gpu_vram_available_gb >= 4:
                return (
                    "medium",  # Whisper medium (~750MB)
                    "facebook/nllb-200-distilled-600M",  # Still distilled for speed
                    "cuda",
                    "float16"
                )
            else:
                return (
                    "small",
                    "facebook/nllb-200-distilled-600M",
                    "cpu",
                    "int8"
                )
        
        # ULTRA profile: Maximum quality
        else:  # HardwareProfile.ULTRA
            if has_gpu and gpu_vram_available_gb and gpu_vram_available_gb >= 6:
                return (
                    "large-v2",  # Whisper large (~1.5GB)
                    "facebook/nllb-200-3.3B",  # Full NLLB model
                    "cuda",
                    "float16"
                )
            else:
                return (
                    "medium",
                    "facebook/nllb-200-distilled-600M",
                    "cpu" if not has_gpu else "cuda",
                    "int8" if not has_gpu else "float16"
                )
    
    def _log_detection_results(self):
        """Log hardware detection results in a nice format"""
        if not self._capabilities:
            return
        
        caps = self._capabilities
        
        logger.info("=" * 60)
        logger.info("🔍 HARDWARE DETECTION RESULTS")
        logger.info("=" * 60)
        
        logger.info(f"💻 CPU: {caps.cpu_count} cores @ {caps.cpu_freq_mhz:.0f} MHz")
        logger.info(
            f"🧠 RAM: {caps.ram_available_gb:.1f}GB available / "
            f"{caps.ram_total_gb:.1f}GB total ({caps.ram_usage_percent:.1f}% used)"
        )
        
        if caps.has_cuda:
            logger.info(
                f"🎮 GPU: {caps.gpu_name} ({caps.gpu_count} device(s))"
            )
            if caps.gpu_memory_total_gb:
                logger.info(
                    f"    VRAM: {caps.gpu_memory_available_gb:.1f}GB available / "
                    f"{caps.gpu_memory_total_gb:.1f}GB total"
                )
        else:
            logger.info("🎮 GPU: Not available (using CPU)")
        
        logger.info(f"📊 Profile: {caps.hardware_profile.value.upper()}")
        logger.info("")
        logger.info("🎯 RECOMMENDED CONFIGURATION:")
        logger.info(f"   • Whisper Model: {caps.recommended_whisper_model}")
        logger.info(f"   • NLLB Model: {caps.recommended_nllb_model}")
        logger.info(f"   • Device: {caps.recommended_device.upper()}")
        logger.info(f"   • Compute Type: {caps.recommended_compute_type}")
        logger.info("=" * 60)
    
    def get_capabilities(self) -> Optional[HardwareCapabilities]:
        """Get cached hardware capabilities (or None if not detected yet)"""
        return self._capabilities
    
    def should_use_gpu(self) -> bool:
        """Check if GPU should be used"""
        if not self._capabilities:
            self.detect()
        return self._capabilities.has_cuda if self._capabilities else False
    
    def get_recommended_whisper_model(self) -> str:
        """Get recommended Whisper model size"""
        if not self._capabilities:
            self.detect()
        return self._capabilities.recommended_whisper_model if self._capabilities else "base"
    
    def get_recommended_nllb_model(self) -> str:
        """Get recommended NLLB model"""
        if not self._capabilities:
            self.detect()
        return self._capabilities.recommended_nllb_model if self._capabilities else "facebook/nllb-200-distilled-600M"
    
    def get_recommended_device(self) -> str:
        """Get recommended device (cuda or cpu)"""
        if not self._capabilities:
            self.detect()
        return self._capabilities.recommended_device if self._capabilities else "cpu"
    
    def get_recommended_compute_type(self) -> str:
        """Get recommended compute type (float16, int8, etc.)"""
        if not self._capabilities:
            self.detect()
        return self._capabilities.recommended_compute_type if self._capabilities else "int8"


# Global singleton instance
hardware_detector = HardwareDetectionService()
