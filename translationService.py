"""
Multilingual support.

Detects the language of an incoming query and, if it isn't English,
translates it to English for intent parsing, then translates the final
response back into the user's language. This is what satisfies the
"Multilingual support for Indian languages" requirement without needing
a Bhashini account — swap `_translate()` for a Bhashini/ULCA call later
if you want official government-endorsed translation.

Both dependencies (langdetect, deep-translator) are lightweight and
pure-Python/HTTP, but if they're unavailable or the network call fails,
everything degrades gracefully to "assume English" rather than crashing
a request.
"""
from typing import Optional

from app.config import get_settings

settings = get_settings()


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return settings.DEFAULT_LANGUAGE
    try:
        from langdetect import detect

        return detect(text)
    except Exception:
        return settings.DEFAULT_LANGUAGE


def translate(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    if not settings.ENABLE_TRANSLATION or not text:
        return text
    if target_lang == (source_lang or "en") == "en":
        return text
    try:
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source=source_lang or "auto", target=target_lang).translate(text)
    except Exception:
        # Network unavailable, language unsupported, dependency missing, etc.
        # Fail open: return the original text rather than breaking the request.
        return text


def to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    return translate(text, target_lang="en", source_lang=source_lang)


def from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    return translate(text, target_lang=target_lang, source_lang="en")
