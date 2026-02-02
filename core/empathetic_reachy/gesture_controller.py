import time
import logging
from typing import List
import numpy as np
from reachy_mini.utils import create_head_pose

logger = logging.getLogger("GestureController")

class GestureController:
    """UPGRADED: Clean, fast gestures with proper antenna handling."""

    def __init__(self, reachy_mini):
        self.mini = reachy_mini
        self.is_moving = False

    def get_available_emotions(self) -> List[str]:
        return ["neutral", "greeting", "thinking", "agreement", "disagreement", 
                "surprised", "confused", "empathy", "happy", "sad", "listening", "excited"]

    def perform_gesture(self, emotion: str):
        """Execute gesture with optimized timing."""
        if self.is_moving: return
        self.is_moving = True
        logger.info(f"Gesture: {emotion}")
        
        try:
            if emotion == "neutral":
                self._move(0, 0, 0, 0, 0, 0.6)
            elif emotion == "greeting":
                self._move(0, -8, 0, 25, 25, 0.3)
                time.sleep(0.2)
                self._move(0, 0, 0, 0, 0, 0.3)
            elif emotion == "thinking":
                self._move(12, -12, 8, 40, -15, 0.8)
                time.sleep(0.5)
                self._move(0, 0, 0, 0, 0, 0.6)
            elif emotion == "agreement":
                for pitch in [12, -8, 0]:
                    self._move(0, pitch, 0, 8, 8, 0.25)
                    time.sleep(0.12)
            elif emotion == "disagreement":
                for yaw in [18, -18, 0]:
                    self._move(yaw, 0, 0, -8, -8, 0.25)
                    time.sleep(0.12)
            elif emotion == "happy":
                self._move(0, -4, 0, 40, 40, 0.4)
                time.sleep(0.25)
                self._move(0, 2, 0, 30, 30, 0.3)
            elif emotion == "excited":
                self._move(8, -8, 0, 50, 50, 0.3)
                time.sleep(0.15)
                self._move(-8, -8, 0, 50, 50, 0.3)
            elif emotion == "sad":
                self._move(0, 15, 0, -25, -25, 1.0)
            elif emotion == "surprised":
                self._move(0, -8, 0, 70, 70, 0.3)
            elif emotion == "confused":
                self._move(0, 0, 15, -5, 35, 0.7)
            elif emotion == "empathy":
                self._move(0, 8, 8, 0, 0, 0.9)
            elif emotion == "listening":
                self._move(0, 4, 0, 15, 15, 0.6)
        except Exception as e:
            logger.error(f"Gesture error: {e}")
        finally:
            self.is_moving = False

    def _move(self, yaw, pitch, roll, ant_l_deg, ant_r_deg, duration):
        """Execute single movement."""
        head_pos = create_head_pose(0, 0, 0, roll, pitch, yaw, mm=True, degrees=True)
        antennas_rad = np.deg2rad([ant_l_deg, ant_r_deg])
        try:
            self.mini.goto_target(head_pos, antennas_rad, duration)
        except Exception as e:
            logger.debug(f"Move error: {e}")