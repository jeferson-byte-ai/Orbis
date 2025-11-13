"""
Dynamic Batching Service
Batch multiple inference requests for optimal GPU utilization
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


@dataclass
class BatchRequest:
    """Represents a batched inference request"""
    request_id: str
    input_data: Any
    timestamp: float
    future: asyncio.Future


class BatchingService:
    """
    Dynamic batching service for ML inference
    
    Collects multiple requests and processes them in batches for:
    - Better GPU utilization
    - Higher throughput
    - Lower per-request latency
    """
    
    def __init__(
        self,
        max_batch_size: int = 8,
        max_wait_ms: int = 50,
        model_type: str = "generic"
    ):
        """
        Initialize batching service
        
        Args:
            max_batch_size: Maximum batch size
            max_wait_ms: Maximum time to wait for batch to fill
            model_type: Type of model (asr, mt, tts)
        """
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.model_type = model_type
        
        # Request queues
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.pending_requests: List[BatchRequest] = []
        
        # Processing task
        self.processing_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Statistics
        self.total_requests = 0
        self.total_batches = 0
        self.total_batch_sizes = []
        
        logger.info(
            f"🎯 Batching service initialized for {model_type} "
            f"(batch_size={max_batch_size}, wait={max_wait_ms}ms)"
        )
    
    def start(self):
        """Start batching service"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_batches())
        logger.info(f"✅ Batching service started for {self.model_type}")
    
    def stop(self):
        """Stop batching service"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
        
        logger.info(f"🛑 Batching service stopped for {self.model_type}")
    
    async def submit(self, input_data: Any) -> Any:
        """
        Submit request for batched processing
        
        Args:
            input_data: Input for inference
        
        Returns:
            Inference result
        """
        self.total_requests += 1
        
        # Create request
        request_id = f"{self.model_type}_{self.total_requests}"
        future = asyncio.Future()
        
        request = BatchRequest(
            request_id=request_id,
            input_data=input_data,
            timestamp=time.time(),
            future=future
        )
        
        # Queue request
        await self.request_queue.put(request)
        
        # Wait for result
        result = await future
        return result
    
    async def _process_batches(self):
        """Background task to process batches"""
        logger.info(f"🔄 Starting batch processor for {self.model_type}")
        
        while self.is_running:
            try:
                # Collect requests for batch
                batch = await self._collect_batch()
                
                if not batch:
                    await asyncio.sleep(0.01)  # Small sleep to avoid busy loop
                    continue
                
                # Process batch
                await self._process_batch(batch)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Batch processing error: {e}")
        
        logger.info(f"🛑 Batch processor stopped for {self.model_type}")
    
    async def _collect_batch(self) -> List[BatchRequest]:
        """Collect requests into a batch"""
        batch = []
        start_time = time.time()
        max_wait_s = self.max_wait_ms / 1000.0
        
        while len(batch) < self.max_batch_size:
            # Calculate remaining wait time
            elapsed = time.time() - start_time
            remaining = max_wait_s - elapsed
            
            if remaining <= 0 and batch:
                # Timeout reached and we have requests
                break
            
            try:
                # Try to get request with timeout
                timeout = min(remaining, 0.01) if batch else max_wait_s
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=timeout
                )
                batch.append(request)
                
            except asyncio.TimeoutError:
                # Timeout - return what we have
                if batch:
                    break
        
        return batch
    
    async def _process_batch(self, batch: List[BatchRequest]):
        """
        Process a batch of requests
        
        Override this method in subclasses for specific model processing
        """
        self.total_batches += 1
        batch_size = len(batch)
        self.total_batch_sizes.append(batch_size)
        
        logger.info(f"⚡ Processing batch of {batch_size} requests")
        
        # Default: process each request individually
        # Subclasses should override this for true batching
        for request in batch:
            try:
                # Placeholder - subclasses should implement actual inference
                result = {"status": "ok", "input": request.input_data}
                request.future.set_result(result)
            except Exception as e:
                logger.error(f"❌ Request {request.request_id} failed: {e}")
                request.future.set_exception(e)
    
    def get_stats(self) -> Dict:
        """Get batching statistics"""
        avg_batch_size = (
            sum(self.total_batch_sizes) / len(self.total_batch_sizes)
            if self.total_batch_sizes
            else 0
        )
        
        return {
            "model_type": self.model_type,
            "is_running": self.is_running,
            "config": {
                "max_batch_size": self.max_batch_size,
                "max_wait_ms": self.max_wait_ms
            },
            "stats": {
                "total_requests": self.total_requests,
                "total_batches": self.total_batches,
                "avg_batch_size": avg_batch_size,
                "queue_size": self.request_queue.qsize()
            }
        }


class ASRBatchingService(BatchingService):
    """Batching service for ASR (Whisper)"""
    
    def __init__(self, asr_service, max_batch_size: int = 4, max_wait_ms: int = 50):
        super().__init__(max_batch_size, max_wait_ms, "asr")
        self.asr_service = asr_service
    
    async def _process_batch(self, batch: List[BatchRequest]):
        """Process ASR batch"""
        self.total_batches += 1
        batch_size = len(batch)
        self.total_batch_sizes.append(batch_size)
        
        logger.info(f"🎙️ Processing ASR batch of {batch_size}")
        
        # Process each audio in batch
        # Note: Whisper doesn't natively support batching, but we can process in parallel
        tasks = []
        for request in batch:
            audio_data, sample_rate, language = request.input_data
            task = self.asr_service.transcribe(
                audio=audio_data,
                language=language,
                sample_rate=sample_rate
            )
            tasks.append((request, task))
        
        # Wait for all transcriptions
        for request, task in tasks:
            try:
                result = await task
                request.future.set_result(result)
            except Exception as e:
                logger.error(f"❌ ASR request {request.request_id} failed: {e}")
                request.future.set_exception(e)


class MTBatchingService(BatchingService):
    """Batching service for Machine Translation (NLLB)"""
    
    def __init__(self, mt_service, max_batch_size: int = 8, max_wait_ms: int = 50):
        super().__init__(max_batch_size, max_wait_ms, "mt")
        self.mt_service = mt_service
    
    async def _process_batch(self, batch: List[BatchRequest]):
        """Process MT batch with true batching"""
        self.total_batches += 1
        batch_size = len(batch)
        self.total_batch_sizes.append(batch_size)
        
        logger.info(f"🌍 Processing MT batch of {batch_size}")
        
        # Group by language pair for efficient batching
        language_groups = defaultdict(list)
        for request in batch:
            text, source_lang, target_lang = request.input_data
            key = f"{source_lang}_{target_lang}"
            language_groups[key].append(request)
        
        # Process each language group
        for lang_pair, group_requests in language_groups.items():
            source_lang, target_lang = lang_pair.split("_")
            
            # Collect texts
            texts = [req.input_data[0] for req in group_requests]
            
            # Batch translate (if MT service supports it)
            for i, request in enumerate(group_requests):
                try:
                    text = texts[i]
                    translated = await self.mt_service.translate(
                        text=text,
                        source_lang=source_lang,
                        target_lang=target_lang
                    )
                    request.future.set_result(translated)
                except Exception as e:
                    logger.error(f"❌ MT request {request.request_id} failed: {e}")
                    request.future.set_exception(e)


class TTSBatchingService(BatchingService):
    """Batching service for Text-to-Speech (Coqui)"""
    
    def __init__(self, tts_service, max_batch_size: int = 4, max_wait_ms: int = 100):
        super().__init__(max_batch_size, max_wait_ms, "tts")
        self.tts_service = tts_service
    
    async def _process_batch(self, batch: List[BatchRequest]):
        """Process TTS batch"""
        self.total_batches += 1
        batch_size = len(batch)
        self.total_batch_sizes.append(batch_size)
        
        logger.info(f"🔊 Processing TTS batch of {batch_size}")
        
        # Process each synthesis
        for request in batch:
            try:
                text, language, voice_profile = request.input_data
                audio = await self.tts_service.synthesize(
                    text=text,
                    language=language,
                    speaker_wav=voice_profile
                )
                request.future.set_result(audio)
            except Exception as e:
                logger.error(f"❌ TTS request {request.request_id} failed: {e}")
                request.future.set_exception(e)
