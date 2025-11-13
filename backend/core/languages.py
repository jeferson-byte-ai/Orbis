"""
Supported Languages for Orbis Translation System
50 most spoken languages worldwide
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Language:
    """Language information"""
    code: str
    name: str
    native_name: str
    flag: str  # Emoji flag


# 50 supported languages
SUPPORTED_LANGUAGES: List[Language] = [
    # Top 20 most spoken
    Language("en", "English", "English", "🇬🇧"),
    Language("zh", "Chinese", "中文", "🇨🇳"),
    Language("hi", "Hindi", "हिन्दी", "🇮🇳"),
    Language("es", "Spanish", "Español", "🇪🇸"),
    Language("ar", "Arabic", "العربية", "🇸🇦"),
    Language("bn", "Bengali", "বাংলা", "🇧🇩"),
    Language("pt", "Portuguese", "Português", "🇧🇷"),
    Language("ru", "Russian", "Русский", "🇷🇺"),
    Language("ja", "Japanese", "日本語", "🇯🇵"),
    Language("pa", "Punjabi", "ਪੰਜਾਬੀ", "🇮🇳"),
    
    # 11-20
    Language("de", "German", "Deutsch", "🇩🇪"),
    Language("jv", "Javanese", "Basa Jawa", "🇮🇩"),
    Language("ko", "Korean", "한국어", "🇰🇷"),
    Language("fr", "French", "Français", "🇫🇷"),
    Language("te", "Telugu", "తెలుగు", "🇮🇳"),
    Language("mr", "Marathi", "मराठी", "🇮🇳"),
    Language("tr", "Turkish", "Türkçe", "🇹🇷"),
    Language("ta", "Tamil", "தமிழ்", "🇮🇳"),
    Language("vi", "Vietnamese", "Tiếng Việt", "🇻🇳"),
    Language("ur", "Urdu", "اردو", "🇵🇰"),
    
    # 21-30
    Language("it", "Italian", "Italiano", "🇮🇹"),
    Language("th", "Thai", "ไทย", "🇹🇭"),
    Language("gu", "Gujarati", "ગુજરાતી", "🇮🇳"),
    Language("pl", "Polish", "Polski", "🇵🇱"),
    Language("uk", "Ukrainian", "Українська", "🇺🇦"),
    Language("ml", "Malayalam", "മലയാളം", "🇮🇳"),
    Language("kn", "Kannada", "ಕನ್ನಡ", "🇮🇳"),
    Language("or", "Odia", "ଓଡ଼ିଆ", "🇮🇳"),
    Language("fa", "Persian", "فارسی", "🇮🇷"),
    Language("my", "Burmese", "မြန်မာ", "🇲🇲"),
    
    # 31-40
    Language("nl", "Dutch", "Nederlands", "🇳🇱"),
    Language("ro", "Romanian", "Română", "🇷🇴"),
    Language("cs", "Czech", "Čeština", "🇨🇿"),
    Language("sv", "Swedish", "Svenska", "🇸🇪"),
    Language("el", "Greek", "Ελληνικά", "🇬🇷"),
    Language("hu", "Hungarian", "Magyar", "🇭🇺"),
    Language("he", "Hebrew", "עברית", "🇮🇱"),
    Language("fi", "Finnish", "Suomi", "🇫🇮"),
    Language("da", "Danish", "Dansk", "🇩🇰"),
    Language("no", "Norwegian", "Norsk", "🇳🇴"),
    
    # 41-50
    Language("id", "Indonesian", "Bahasa Indonesia", "🇮🇩"),
    Language("ms", "Malay", "Bahasa Melayu", "🇲🇾"),
    Language("fil", "Filipino", "Filipino", "🇵🇭"),
    Language("sw", "Swahili", "Kiswahili", "🇰🇪"),
    Language("bg", "Bulgarian", "Български", "🇧🇬"),
    Language("sk", "Slovak", "Slovenčina", "🇸🇰"),
    Language("hr", "Croatian", "Hrvatski", "🇭🇷"),
    Language("sr", "Serbian", "Српски", "🇷🇸"),
    Language("lt", "Lithuanian", "Lietuvių", "🇱🇹"),
    Language("sl", "Slovenian", "Slovenščina", "🇸🇮"),
]

# Create lookup dictionaries
LANGUAGES_BY_CODE: Dict[str, Language] = {lang.code: lang for lang in SUPPORTED_LANGUAGES}
LANGUAGES_BY_NAME: Dict[str, Language] = {lang.name.lower(): lang for lang in SUPPORTED_LANGUAGES}


def get_language(code: str) -> Language | None:
    """Get language by code"""
    return LANGUAGES_BY_CODE.get(code)


def get_language_name(code: str) -> str:
    """Get language name by code"""
    lang = get_language(code)
    return lang.name if lang else code


def get_language_native_name(code: str) -> str:
    """Get native language name by code"""
    lang = get_language(code)
    return lang.native_name if lang else code


def validate_language_code(code: str) -> bool:
    """Check if language code is supported"""
    return code in LANGUAGES_BY_CODE or code == "auto"


def get_supported_language_codes() -> List[str]:
    """Get list of supported language codes"""
    return list(LANGUAGES_BY_CODE.keys())


def get_languages_for_api() -> List[Dict[str, str]]:
    """Get languages formatted for API response"""
    return [
        {
            "code": lang.code,
            "name": lang.name,
            "native_name": lang.native_name,
            "flag": lang.flag
        }
        for lang in SUPPORTED_LANGUAGES
    ]
