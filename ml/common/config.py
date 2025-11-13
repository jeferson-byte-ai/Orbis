"""ML configuration"""
from pydantic_settings import BaseSettings
from typing import Literal


class MLSettings(BaseSettings):
    """ML service settings"""
    
    # ASR
    asr_model: str = "openai/whisper-large-v3-turbo"
    asr_device: Literal["cuda", "cpu"] = "cuda"
    asr_compute_type: Literal["float16", "int8", "float32"] = "float16"
    asr_batch_size: int = 8
    
    # MT
    mt_model: str = "facebook/nllb-200-distilled-600M"
    mt_device: Literal["cuda", "cpu"] = "cuda"
    mt_batch_size: int = 16
    
    # TTS
    tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    tts_device: Literal["cuda", "cpu"] = "cuda"
    tts_streaming: bool = True
    
    # Performance
    target_latency_ms: int = 250
    enable_caching: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


ml_settings = MLSettings()
