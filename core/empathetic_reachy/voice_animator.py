import asyncio
import numpy as np
import logging
from reachy_mini.utils import create_head_pose

logger = logging.getLogger("VoiceAnimator")

class VoiceAnimator:
    """PERFECT: Balanced, natural movements."""
    
    def __init__(self, reachy_mini):
        self.mini = reachy_mini
        self.is_animating = False

    async def animate_speech(self, duration: float):
        """Smooth natural movements."""
        self.is_animating = True
        start_time = asyncio.get_event_loop().time()
        phase = 0
        
        try:
            while self.is_animating and (asyncio.get_event_loop().time() - start_time) < duration:
                t = phase
                yaw = np.sin(t * 1.0) * 4
                pitch = np.sin(t * 1.4) * 2
                roll = np.sin(t * 0.7) * 1.5
                
                ant_base = 18
                ant_l = ant_base + np.sin(t * 1.8) * 12
                ant_r = ant_base - np.sin(t * 1.8) * 12
                
                try:
                    head_pos = create_head_pose(0, 0, 0, roll, pitch, yaw, mm=True, degrees=True)
                    antennas = np.deg2rad([ant_l, ant_r])
                    self.mini.goto_target(head_pos, antennas, duration=0.1)
                except Exception as e:
                    logger.debug(f"Skip: {e}")
                
                phase += 0.18
                await asyncio.sleep(0.1)
        finally:
            self.stop_animation()

    def stop_animation(self):
        """Reset."""
        self.is_animating = False
        try:
            head_pos = create_head_pose(0, 0, 0, 0, 0, 0, mm=True, degrees=True)
            self.mini.goto_target(head_pos, np.deg2rad([0, 0]), duration=0.3)
        except Exception as e:
            logger.debug(f"Reset skip: {e}")