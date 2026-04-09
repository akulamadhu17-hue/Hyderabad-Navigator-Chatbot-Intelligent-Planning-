"""
Hyderabad Navigator - Voice Handler
Speech-to-Text and Text-to-Speech support
"""

import os
import base64
import tempfile

# ─── Text-to-Speech ───────────────────────────────────────────────────────────

LANG_CODES = {"en": "en-IN", "hi": "hi", "te": "te"}

def text_to_speech_base64(text: str, lang: str = "en") -> str | None:
    """
    Convert text to speech and return base64-encoded MP3.
    Requires: pip install gTTS
    """
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=LANG_CODES.get(lang, "en-IN"), slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        tts.save(tmp_path)
        with open(tmp_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        os.unlink(tmp_path)
        return audio_b64
    except ImportError:
        return None
    except Exception as e:
        print(f"TTS error: {e}")
        return None


# ─── Speech-to-Text ───────────────────────────────────────────────────────────

def speech_to_text(audio_bytes: bytes, lang: str = "en") -> str | None:
    """
    Convert audio bytes to text using SpeechRecognition.
    Requires: pip install SpeechRecognition
    """
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
        os.unlink(tmp_path)
        lang_code = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}.get(lang, "en-IN")
        text = recognizer.recognize_google(audio, language=lang_code)
        return text
    except ImportError:
        return None
    except Exception as e:
        print(f"STT error: {e}")
        return None
