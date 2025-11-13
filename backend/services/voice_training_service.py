"""Voice training service
Handles background processing to convert uploaded audio into usable voice profiles."""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

from backend.config import settings
from backend.db.models import VoiceProfile
from backend.db.session import SessionLocal
from ml.tts.coqui_service import coqui_service

logger = logging.getLogger(__name__)


async def train_voice_profile(voice_id: UUID, audio_sample_path: str) -> None:
    """Train (or simulate training) of a cloned voice profile.

    Updates the corresponding database record with progress and completion state.
    """

    session = SessionLocal()
    try:
        voice: Optional[VoiceProfile] = (
            session.query(VoiceProfile).filter(VoiceProfile.id == voice_id).first()
        )
        if voice is None:
            logger.warning("Voice profile %s not found for training", voice_id)
            return

        logger.info("Starting training for voice profile %s", voice_id)

        artifact_path = Path(settings.voices_path) / f"{voice_id}.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize progress markers to provide user feedback
        for progress in (5.0, 20.0, 55.0):
            voice.training_progress = progress
            session.commit()
            await asyncio.sleep(0.5)

        # Ensure the TTS model is ready; load lazily and continue even if it fails
        try:
            if coqui_service.tts is None:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, coqui_service.load)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Coqui TTS load failed: %s", exc)

        success = False
        try:
            success = await coqui_service.clone_voice([audio_sample_path], str(artifact_path))
        except Exception as exc:  # noqa: BLE001
            logger.error("Voice cloning failed for %s: %s", voice_id, exc)

        voice.model_path = str(artifact_path) if success else None
        voice.is_ready = success
        voice.training_progress = 100.0 if success else 0.0
        if success and voice.quality_score is None:
            voice.quality_score = 82.0

        session.commit()

        logger.info(
            "Voice profile %s training %s", voice_id, "completed" if success else "failed"
        )

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error during voice training for %s: %s", voice_id, exc)
    finally:
        session.close()
