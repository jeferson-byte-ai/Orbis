"""ML utilities"""
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def measure_latency(func):
    """Decorator to measure function latency"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        latency_ms = (time.time() - start) * 1000
        logger.info(f"{func.__name__} latency: {latency_ms:.2f}ms")
        return result, latency_ms
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        latency_ms = (time.time() - start) * 1000
        logger.info(f"{func.__name__} latency: {latency_ms:.2f}ms")
        return result, latency_ms
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def check_gpu_availability():
    """Check if GPU is available"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_device(preferred: str = "cuda"):
    """Get compute device (cuda or cpu)"""
    if preferred == "cuda" and check_gpu_availability():
        return "cuda"
    return "cpu"
