import os
import sys
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()

# --- API KEYS ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# --- SIMULATION SETTINGS ---
# Detect simulation mode via flag or env var
SIMULATION_MODE = "--sim" in sys.argv or os.getenv("REACHY_SIMULATION", "false").lower() == "true"

# --- AUDIO SETTINGS ---
STT_ENGINE = "whisper"  # Speech-to-Text: Whisper (local, free)
TTS_ENGINE = "gtts"  # Text-to-Speech: gTTS (free, no API needed)
WHISPER_MODEL = "base"
AUDIO_SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5
AUDIO_INPUT_DEVICE = None  # None = system default, or set device index/name
AUDIO_BUFFER_SIZE = 2048  # Larger = smoother playback (prevents stuttering)

# --- ROBOT SETTINGS ---
MAX_CONVERSATION_HISTORY = 20
GESTURE_DURATION = 1.5

# Safe limits for Reachy Mini
HEAD_LIMITS = {
    'pitch': (-20, 20),
    'roll': (-20, 20),
    'yaw': (-40, 40)
}
ANTENNA_RANGE = (-30, 30)  # Degrees

def validate_config():
    """Validates critical configuration."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

def print_config():
    """Prints current configuration status."""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 EMPATHETIC REACHY CONFIGURATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Mode: {'SIMULATION' if SIMULATION_MODE else 'HARDWARE'}")
    print(f"Anthropic Key: {'✅ Set' if ANTHROPIC_API_KEY else '❌ Missing'}")
    print(f"Nvidia Key: {'✅ Set' if NVIDIA_API_KEY else '⚠️ Optional (Missing)'}")
    print(f"STT Engine: {STT_ENGINE} ({WHISPER_MODEL})")
    print(f"TTS Engine: {TTS_ENGINE} (free, no API needed)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")