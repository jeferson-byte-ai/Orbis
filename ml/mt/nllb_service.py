"""
NLLB Machine Translation Service
Translates text between 200+ languages
"""
import logging
from typing import Dict, Optional
import torch

logger = logging.getLogger(__name__)


class NLLBService:
    """NLLB translation service for real-time text translation"""
    
    # Language code mapping (ISO 639-1 to NLLB codes)
    LANG_CODES = {
        'en': 'eng_Latn',
        'pt': 'por_Latn',
        'es': 'spa_Latn',
        'fr': 'fra_Latn',
        'de': 'deu_Latn',
        'it': 'ita_Latn',
        'ja': 'jpn_Jpan',
        'ko': 'kor_Hang',
        'zh': 'zho_Hans',
        'ar': 'arb_Arab',
        'ru': 'rus_Cyrl',
        'hi': 'hin_Deva',
        'nl': 'nld_Latn',
        'pl': 'pol_Latn',
        'tr': 'tur_Latn',
        'sv': 'swe_Latn',
        'no': 'nob_Latn',
        'da': 'dan_Latn',
        'fi': 'fin_Latn'
    }
    
    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M", device: str = "cuda"):
        """
        Initialize NLLB service
        
        Args:
            model_name: NLLB model to use
            device: Device to run on (cuda or cpu)
        """
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        logger.info(f"Initializing NLLB MT: {model_name} on {self.device}")
    
    def load(self):
        """Load translation model"""
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            if self.device == "cuda":
                self.model = self.model.to(self.device)
                self.model = self.model.half()  # Use FP16 for speed
            
            self.model.eval()
            logger.info("✅ NLLB model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load NLLB model: {e}")
            raise
    
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        max_length: int = 400
    ) -> str:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (ISO 639-1)
            target_lang: Target language code (ISO 639-1)
            max_length: Maximum output length
        
        Returns:
            Translated text
        """
        try:
            # Skip if same language
            if source_lang == target_lang:
                return text
            
            # Convert language codes
            src_code = self.LANG_CODES.get(source_lang, 'eng_Latn')
            tgt_code = self.LANG_CODES.get(target_lang, 'eng_Latn')
            
            # Mock translation for now (until model is loaded)
            if self.model is None:
                logger.warning("Model not loaded, using mock translation")
                return f"[{target_lang.upper()}] {text}"
            
            # Tokenize input
            self.tokenizer.src_lang = src_code
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True,
                truncation=True,
                max_length=512
            )
            
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_code],
                    max_length=max_length,
                    num_beams=5,
                    early_stopping=True
                )
            
            # Decode translation
            translated_text = self.tokenizer.batch_decode(
                translated_tokens, 
                skip_special_tokens=True
            )[0]
            
            logger.info(f"Translated: '{text}' → '{translated_text}' ({source_lang}→{target_lang})")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Fallback to original text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {code: f"Language {code}" for code in self.LANG_CODES.keys()}


# Singleton instance
nllb_service = NLLBService()