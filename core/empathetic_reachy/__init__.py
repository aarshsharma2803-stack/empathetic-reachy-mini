"""Empathetic Reachy - Conversational robot system"""
__version__ = "1.0.0"

from . import config
from .conversation_manager import ConversationManager
from .emotion_analyzer import EmotionAnalyzer
from .gesture_controller import GestureController
from .head_mirroring import HeadMirroringController
from .voice_animator import VoiceAnimator

__all__ = [
    "config",
    "ConversationManager",
    "EmotionAnalyzer", 
    "GestureController",
    "HeadMirroringController",
    "VoiceAnimator",
]