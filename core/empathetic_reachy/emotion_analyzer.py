import re
import logging
import random
from textblob import TextBlob # type: ignore
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmotionAnalyzer")

class EmotionAnalyzer:
    """
    3-tier emotion detection system:
    1. Keyword/Regex (Instant)
    2. Nemotron API (Optional/Skipped in Sim)
    3. TextBlob Sentiment (Fallback)
    """

    EMOTIONS = [
        "neutral", "happy", "sad", "angry", "surprised", 
        "confused", "excited", "thinking", "agreement", 
        "disagreement", "empathy", "listening"
    ]

    # Keyword mappings for instant detection
    KEYWORD_MAP = {
        r"\b(hi|hello|hey|greetings)\b": "greeting",
        r"\b(yes|yeah|sure|okay)\b": "agreement",
        r"\b(no|nope|not)\b": "disagreement",
        r"\b(wow|whoa|amazing)\b": "surprised",
        r"\b(what|huh|why)\b": "confused",
        r"\b(sorry|understand|feel)\b": "empathy",
        r"\b(great|awesome|love|good)\b": "happy",
        r"\b(bad|terrible|sad|cry)\b": "sad",
        r"\b(wait|let me see|hmm)\b": "thinking",
    }

    def __init__(self, nvidia_api_key: Optional[str] = None, simulation_mode: bool = True):
        self.nvidia_api_key = nvidia_api_key
        self.simulation_mode = simulation_mode
        self._cache = {}
        self.metrics = {"total": 0, "keyword": 0, "api": 0, "fallback": 0}

    def analyze(self, text: str) -> str:
        """Analyze text and return the dominant emotion."""
        emotion, _ = self.analyze_with_confidence(text)
        return emotion

    def analyze_with_confidence(self, text: str) -> Tuple[str, float]:
        """Returns (emotion, confidence)."""
        text_lower = text.lower()
        self.metrics["total"] += 1

        # 1. Cache Check
        if text_lower in self._cache:
            return self._cache[text_lower]

        # 2. Keyword Detection
        for pattern, emotion in self.KEYWORD_MAP.items():
            if re.search(pattern, text_lower):
                self.metrics["keyword"] += 1
                logger.info(f"Emotion (Keyword): {emotion}")
                return emotion, 0.9

        # 3. Sentiment Analysis (Fallback)
        # Using TextBlob for simple polarity/subjectivity
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        emotion = "neutral"
        confidence = 0.5

        if polarity > 0.5:
            emotion = "excited"
            confidence = 0.7
        elif polarity > 0.1:
            emotion = "happy"
            confidence = 0.6
        elif polarity < -0.5:
            emotion = "sad"
            confidence = 0.7
        elif polarity < -0.1:
            emotion = "empathy" # Often negative sentiment in empathy (e.g. "I'm sorry")
            confidence = 0.5
        
        self.metrics["fallback"] += 1
        
        # Cache result
        self._cache[text_lower] = (emotion, confidence)
        logger.info(f"Emotion (TextBlob): {emotion} ({polarity})")
        return emotion, confidence

    def get_gesture_for_emotion(self, emotion: str) -> str:
        """Maps an emotion string to a valid gesture command."""
        if emotion == "greeting": return "greeting"
        if emotion in self.EMOTIONS: return emotion
        return "neutral"