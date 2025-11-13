"""
Real-time ML Pipeline for ASR -> MT -> TTS
Optimized for ultra-low latency (<100ms)
"""
import asyncio
import logging
import time
import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AudioChunk:
    """Represents an audio chunk for processing"""
    data: np.ndarray
    sample_rate: int
    timestamp: float
    participant_id: str
    room_id: str
    source_language: str


@dataclass
class TranscriptionResult:
    """ASR transcription result"""
    text: str
    language: str
    confidence: float
    latency_ms: float
    timestamp: float


@dataclass
class TranslationResult:
    """MT translation result"""
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    latency_ms: float


@dataclass
class SynthesisResult:
    """TTS synthesis result"""
    audio: np.ndarray
    text: str
    language: str
    latency_ms: float


class MLPipeline:
    """
    Production-ready ML Pipeline for real-time translation
    
    Pipeline: Audio -> ASR (transcribe) -> MT (translate) -> TTS (synthesize) -> Audio
    Target latency: <100ms end-to-end
    """
    
    def __init__(self):
        self.asr_service = None
        self.mt_service = None
        self.tts_service = None
        
        # Performance tracking
        self.pipeline_latencies = deque(maxlen=100)
        self.asr_latencies = deque(maxlen=100)
        self.mt_latencies = deque(maxlen=100)
        self.tts_latencies = deque(maxlen=100)
        
        # Caching
        self.translation_cache: Dict[str, str] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("🤖 ML Pipeline initialized")
    
    async def initialize(self):
        """Initialize all ML services"""
        logger.info("🚀 Initializing ML services...")
        
        try:
            # Import services
            from ml.asr.whisper_service import whisper_service
            from ml.mt.nllb_service import nllb_service
            from ml.tts.coqui_service import coqui_service
            
            self.asr_service = whisper_service
            self.mt_service = nllb_service
            self.tts_service = coqui_service
            
            # Load models in parallel for speed
            load_tasks = []
            
            if not getattr(self.asr_service, "model_loaded", False):
                load_tasks.append(self._load_asr())
            
            if self.mt_service.model is None:
                load_tasks.append(self._load_mt())
            
            if self.tts_service.tts is None:
                load_tasks.append(self._load_tts())
            
            if load_tasks:
                await asyncio.gather(*load_tasks, return_exceptions=True)
            
            logger.info("✅ All ML services initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML services: {e}")
            raise
    
    async def _load_asr(self):
        """Load ASR model"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.asr_service.load)
            logger.info("✅ ASR service ready")
        except Exception as e:
            logger.error(f"❌ ASR loading failed: {e}")
    
    async def _load_mt(self):
        """Load MT model"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.mt_service.load)
            logger.info("✅ MT service ready")
        except Exception as e:
            logger.error(f"❌ MT loading failed: {e}")
    
    async def _load_tts(self):
        """Load TTS model"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.tts_service.load)
            logger.info("✅ TTS service ready")
        except Exception as e:
            logger.error(f"❌ TTS loading failed: {e}")
    
    async def process_audio_chunk(
        self,
        audio_chunk: AudioChunk,
        target_languages: List[str],
        voice_profile: Optional[str] = None
    ) -> Dict[str, SynthesisResult]:
        """
        Process audio chunk through full pipeline
        
        Args:
            audio_chunk: Input audio chunk
            target_languages: List of target languages
            voice_profile: Optional voice profile for TTS
        
        Returns:
            Dict mapping language code to synthesis result
        """
        pipeline_start = time.time()
        results = {}
        
        try:
            # Step 1: ASR (Speech to Text)
            transcription = await self._transcribe(audio_chunk)
            if not transcription or not transcription.text.strip():
                logger.debug("Empty transcription, skipping pipeline")
                return results
            
            # Step 2: MT (Text Translation)
            translations = await self._translate(
                transcription.text,
                transcription.language,
                target_languages
            )
            
            # Step 3: TTS (Text to Speech)
            for target_lang, translation in translations.items():
                synthesis = await self._synthesize(
                    translation.translated_text,
                    target_lang,
                    voice_profile
                )
                if synthesis:
                    results[target_lang] = synthesis
            
            # Track performance
            pipeline_latency = (time.time() - pipeline_start) * 1000
            self.pipeline_latencies.append(pipeline_latency)
            
            logger.info(
                f"✅ Pipeline completed in {pipeline_latency:.0f}ms | "
                f"ASR: {transcription.latency_ms:.0f}ms | "
                f"Targets: {len(results)}"
            )
            
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
        
        return results
    
    async def _transcribe(self, audio_chunk: AudioChunk) -> Optional[TranscriptionResult]:
        """Transcribe audio to text"""
        if not self.asr_service or not getattr(self.asr_service, "model_loaded", False):
            logger.warning("ASR service not ready")
            return None
        
        try:
            start = time.time()
            
            text, detected_lang, metadata = await self.asr_service.transcribe(
                audio=audio_chunk.data,
                language=audio_chunk.source_language,
                sample_rate=audio_chunk.sample_rate,
                vad_filter=True
            )
            
            latency = (time.time() - start) * 1000
            self.asr_latencies.append(latency)
            
            return TranscriptionResult(
                text=text,
                language=detected_lang,
                confidence=metadata.get("language_probability", 0.0),
                latency_ms=latency,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")
            return None
    
    async def _translate(
        self,
        text: str,
        source_lang: str,
        target_languages: List[str]
    ) -> Dict[str, TranslationResult]:
        """Translate text to multiple languages"""
        if not self.mt_service:
            logger.warning("MT service not ready")
            return {}
        
        results = {}
        
        for target_lang in target_languages:
            # Skip if same language
            if target_lang == source_lang:
                results[target_lang] = TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    latency_ms=0
                )
                continue
            
            # Check cache
            cache_key = f"{source_lang}:{target_lang}:{text}"
            if cache_key in self.translation_cache:
                self.cache_hits += 1
                translated = self.translation_cache[cache_key]
                results[target_lang] = TranslationResult(
                    original_text=text,
                    translated_text=translated,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    latency_ms=0
                )
                continue
            
            # Translate
            try:
                start = time.time()
                
                translated = await self.mt_service.translate(
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                
                latency = (time.time() - start) * 1000
                self.mt_latencies.append(latency)
                
                # Cache result
                self.translation_cache[cache_key] = translated
                self.cache_misses += 1
                
                # Limit cache size
                if len(self.translation_cache) > 1000:
                    # Remove oldest entries (first 100)
                    for key in list(self.translation_cache.keys())[:100]:
                        del self.translation_cache[key]
                
                results[target_lang] = TranslationResult(
                    original_text=text,
                    translated_text=translated,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    latency_ms=latency
                )
                
            except Exception as e:
                logger.error(f"❌ Translation error ({source_lang}->{target_lang}): {e}")
        
        return results
    
    async def _synthesize(
        self,
        text: str,
        language: str,
        voice_profile: Optional[str] = None
    ) -> Optional[SynthesisResult]:
        """Synthesize speech from text"""
        if not self.tts_service:
            logger.warning("TTS service not ready")
            return None
        
        try:
            start = time.time()
            
            audio = await self.tts_service.synthesize(
                text=text,
                language=language,
                speaker_wav=voice_profile
            )
            
            latency = (time.time() - start) * 1000
            self.tts_latencies.append(latency)
            
            return SynthesisResult(
                audio=audio,
                text=text,
                language=language,
                latency_ms=latency
            )
            
        except Exception as e:
            logger.error(f"❌ Synthesis error: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics"""
        def calc_stats(latencies):
            if not latencies:
                return {"count": 0}
            return {
                "count": len(latencies),
                "avg_ms": sum(latencies) / len(latencies),
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "last_ms": latencies[-1]
            }
        
        cache_total = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            "pipeline": calc_stats(self.pipeline_latencies),
            "asr": calc_stats(self.asr_latencies),
            "mt": calc_stats(self.mt_latencies),
            "tts": calc_stats(self.tts_latencies),
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate_pct": cache_hit_rate,
                "size": len(self.translation_cache)
            }
        }


# Singleton instance
ml_pipeline = MLPipeline()
