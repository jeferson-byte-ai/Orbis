"""
SFU Configuration
High-performance WebRTC Selective Forwarding Unit configuration
"""
import os
from typing import Dict, List
from pydantic_settings import BaseSettings


class SFUConfig(BaseSettings):
    """SFU Configuration with production-grade settings"""
    
    # Server Configuration
    listen_ip: str = "0.0.0.0"
    listen_port: int = 3000
    announced_ip: str = os.getenv("SFU_ANNOUNCED_IP", "127.0.0.1")
    
    # WebRTC Configuration
    rtc_min_port: int = 40000
    rtc_max_port: int = 49999
    
    # Media Configuration
    audio_codec: str = "opus"
    video_codec: str = "vp8"
    audio_sample_rate: int = 48000
    audio_channels: int = 2
    
    # Performance Settings
    max_rooms: int = 1000
    max_participants_per_room: int = 100
    max_producers_per_participant: int = 4
    max_consumers_per_participant: int = 40
    
    # Quality Settings
    audio_bitrate: int = 128000  # 128 kbps
    video_bitrate: int = 2000000  # 2 Mbps
    
    # Network Settings
    enable_tcp: bool = True
    enable_udp: bool = True
    prefer_udp: bool = True
    
    # TURN/STUN Configuration
    stun_servers: List[str] = ["stun:stun.l.google.com:19302"]
    turn_servers: List[Dict] = []
    
    # Security
    enable_dtls: bool = True
    enable_srtp: bool = True
    
    # Monitoring
    enable_stats: bool = True
    stats_interval: int = 5  # seconds
    
    # Redis for scaling
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # ML Integration
    enable_asr: bool = True
    enable_translation: bool = True
    enable_tts: bool = True
    
    # Latency targets (milliseconds)
    target_e2e_latency_ms: int = 150  # End-to-end including ML
    target_network_latency_ms: int = 50  # Network only
    target_ml_latency_ms: int = 100  # ML processing
    
    class Config:
        env_prefix = "SFU_"


sfu_config = SFUConfig()
