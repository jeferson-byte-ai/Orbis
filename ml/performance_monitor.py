"""
Performance Monitoring for ML Services
Real-time metrics, profiling, and optimization recommendations
"""
import asyncio
import logging
import time
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    
    # Latency metrics (milliseconds)
    asr_latency_ms: Optional[float] = None
    mt_latency_ms: Optional[float] = None
    tts_latency_ms: Optional[float] = None
    e2e_latency_ms: Optional[float] = None
    
    # Throughput metrics
    asr_requests_per_sec: float = 0.0
    mt_requests_per_sec: float = 0.0
    tts_requests_per_sec: float = 0.0
    
    # Resource utilization
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    gpu_memory_mb: Optional[float] = None
    
    # Quality metrics
    transcription_confidence: Optional[float] = None


class PerformanceMonitor:
    """
    Monitors and analyzes ML pipeline performance
    
    Features:
    - Real-time metrics collection
    - Performance profiling
    - Bottleneck detection
    - Optimization recommendations
    - Alert generation
    """
    
    def __init__(self, window_size: int = 100, alert_threshold_ms: int = 200):
        self.window_size = window_size
        self.alert_threshold_ms = alert_threshold_ms
        
        # Metric storage
        self.metrics_history: deque = deque(maxlen=window_size)
        self.asr_latencies: deque = deque(maxlen=window_size)
        self.mt_latencies: deque = deque(maxlen=window_size)
        self.tts_latencies: deque = deque(maxlen=window_size)
        self.e2e_latencies: deque = deque(maxlen=window_size)
        
        # Counters
        self.asr_requests = 0
        self.mt_requests = 0
        self.tts_requests = 0
        self.alerts_generated = 0
        
        # Timing
        self.start_time = time.time()
        self.last_report_time = time.time()
        
        logger.info("📊 Performance monitor initialized")
    
    def record_asr_latency(self, latency_ms: float):
        """Record ASR latency"""
        self.asr_latencies.append(latency_ms)
        self.asr_requests += 1
        
        if latency_ms > self.alert_threshold_ms:
            self._generate_alert("ASR", latency_ms)
    
    def record_mt_latency(self, latency_ms: float):
        """Record MT latency"""
        self.mt_latencies.append(latency_ms)
        self.mt_requests += 1
        
        if latency_ms > self.alert_threshold_ms:
            self._generate_alert("MT", latency_ms)
    
    def record_tts_latency(self, latency_ms: float):
        """Record TTS latency"""
        self.tts_latencies.append(latency_ms)
        self.tts_requests += 1
        
        if latency_ms > self.alert_threshold_ms:
            self._generate_alert("TTS", latency_ms)
    
    def record_e2e_latency(self, latency_ms: float):
        """Record end-to-end latency"""
        self.e2e_latencies.append(latency_ms)
        
        if latency_ms > self.alert_threshold_ms * 1.5:
            self._generate_alert("E2E", latency_ms)
    
    def _generate_alert(self, component: str, latency_ms: float):
        """Generate performance alert"""
        self.alerts_generated += 1
        logger.warning(
            f"⚠️ PERFORMANCE ALERT: {component} latency {latency_ms:.0f}ms "
            f"exceeds threshold {self.alert_threshold_ms}ms"
        )
    
    async def collect_snapshot(self) -> PerformanceMetrics:
        """Collect current performance snapshot"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # GPU metrics
        gpu_memory_mb = None
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory_mb = torch.cuda.memory_allocated() / 1024**2
        except ImportError:
            pass
        
        # Latency metrics
        snapshot = PerformanceMetrics(
            timestamp=time.time(),
            asr_latency_ms=self._calc_avg(self.asr_latencies),
            mt_latency_ms=self._calc_avg(self.mt_latencies),
            tts_latency_ms=self._calc_avg(self.tts_latencies),
            e2e_latency_ms=self._calc_avg(self.e2e_latencies),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            gpu_memory_mb=gpu_memory_mb
        )
        
        self.metrics_history.append(snapshot)
        return snapshot
    
    def _calc_avg(self, values: deque) -> Optional[float]:
        """Calculate average of values"""
        if not values:
            return None
        return sum(values) / len(values)
    
    def _calc_p95(self, values: deque) -> Optional[float]:
        """Calculate 95th percentile"""
        if not values:
            return None
        sorted_values = sorted(values)
        index = int(len(sorted_values) * 0.95)
        return sorted_values[index] if index < len(sorted_values) else sorted_values[-1]
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        uptime_seconds = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime_seconds,
            "total_requests": {
                "asr": self.asr_requests,
                "mt": self.mt_requests,
                "tts": self.tts_requests
            },
            "latency_stats": {
                "asr": self._get_latency_stats(self.asr_latencies),
                "mt": self._get_latency_stats(self.mt_latencies),
                "tts": self._get_latency_stats(self.tts_latencies),
                "e2e": self._get_latency_stats(self.e2e_latencies)
            },
            "throughput": {
                "asr_rps": self.asr_requests / uptime_seconds if uptime_seconds > 0 else 0,
                "mt_rps": self.mt_requests / uptime_seconds if uptime_seconds > 0 else 0,
                "tts_rps": self.tts_requests / uptime_seconds if uptime_seconds > 0 else 0
            },
            "alerts": {
                "total": self.alerts_generated,
                "threshold_ms": self.alert_threshold_ms
            }
        }
    
    def _get_latency_stats(self, latencies: deque) -> Dict:
        """Get detailed latency statistics"""
        if not latencies:
            return {
                "count": 0,
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "p95_ms": 0
            }
        
        return {
            "count": len(latencies),
            "avg_ms": sum(latencies) / len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "p95_ms": self._calc_p95(latencies) or 0
        }
    
    def analyze_bottlenecks(self) -> List[Dict]:
        """Analyze and identify performance bottlenecks"""
        bottlenecks = []
        
        # Check ASR latency
        asr_avg = self._calc_avg(self.asr_latencies)
        if asr_avg and asr_avg > 100:
            bottlenecks.append({
                "component": "ASR",
                "severity": "high" if asr_avg > 200 else "medium",
                "avg_latency_ms": asr_avg,
                "recommendation": "Consider using smaller Whisper model (tiny/base) or enable GPU"
            })
        
        # Check MT latency
        mt_avg = self._calc_avg(self.mt_latencies)
        if mt_avg and mt_avg > 150:
            bottlenecks.append({
                "component": "MT",
                "severity": "high" if mt_avg > 300 else "medium",
                "avg_latency_ms": mt_avg,
                "recommendation": "Enable FP16, use smaller model, or implement caching"
            })
        
        # Check TTS latency
        tts_avg = self._calc_avg(self.tts_latencies)
        if tts_avg and tts_avg > 200:
            bottlenecks.append({
                "component": "TTS",
                "severity": "high" if tts_avg > 400 else "medium",
                "avg_latency_ms": tts_avg,
                "recommendation": "Consider streaming TTS or pre-generating common phrases"
            })
        
        # Check system resources
        if self.metrics_history:
            latest = self.metrics_history[-1]
            
            if latest.cpu_percent > 90:
                bottlenecks.append({
                    "component": "CPU",
                    "severity": "high",
                    "value": latest.cpu_percent,
                    "recommendation": "Scale horizontally or upgrade CPU"
                })
            
            if latest.memory_percent > 90:
                bottlenecks.append({
                    "component": "Memory",
                    "severity": "high",
                    "value": latest.memory_percent,
                    "recommendation": "Add more RAM or reduce model sizes"
                })
        
        return bottlenecks
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        # Analyze bottlenecks
        bottlenecks = self.analyze_bottlenecks()
        
        if not bottlenecks:
            recommendations.append("✅ System performing well - no major bottlenecks detected")
            return recommendations
        
        # General recommendations
        recommendations.append("🎯 Optimization Recommendations:")
        
        for bottleneck in bottlenecks:
            recommendations.append(
                f"  - {bottleneck['component']}: {bottleneck['recommendation']}"
            )
        
        # Additional recommendations based on metrics
        asr_avg = self._calc_avg(self.asr_latencies)
        mt_avg = self._calc_avg(self.mt_latencies)
        tts_avg = self._calc_avg(self.tts_latencies)
        
        if asr_avg and mt_avg and tts_avg:
            total_avg = asr_avg + mt_avg + tts_avg
            
            if total_avg > 500:
                recommendations.append("  - Consider pipeline parallelization")
                recommendations.append("  - Implement request batching")
                recommendations.append("  - Use model quantization (INT8/FP16)")
        
        return recommendations


# Singleton instance
performance_monitor = PerformanceMonitor(window_size=100, alert_threshold_ms=150)
