# ============================================================================
# backend/utils/voice_alert.py - Voice Alert System
# ============================================================================

import pyttsx3
from backend.utils.logger import setup_logger
import threading

logger = setup_logger(__name__)

# Initialize TTS engine (singleton)
_tts_engine = None
_tts_lock = threading.Lock()

def get_tts_engine():
    """Get or create TTS engine"""
    global _tts_engine
    if _tts_engine is None:
        with _tts_lock:
            if _tts_engine is None:
                _tts_engine = pyttsx3.init()
                _tts_engine.setProperty('rate', 150)  # Speech rate
                _tts_engine.setProperty('volume', 0.9)  # Volume (0-1)
    return _tts_engine

def speak_alert(message: str, async_speak: bool = True):
    """
    Speak alert message using text-to-speech
    
    Args:
        message: Text to speak
        async_speak: If True, speak in background thread
    """
    try:
        engine = get_tts_engine()
        
        def _speak():
            try:
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        if async_speak:
            thread = threading.Thread(target=_speak)
            thread.daemon = True
            thread.start()
        else:
            _speak()
        
        logger.info(f"Voice alert: {message[:50]}...")
        
    except Exception as e:
        logger.error(f"Failed to speak alert: {e}")
