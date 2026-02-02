import asyncio
import io
import logging
import tempfile
import time
import os
import wave
from typing import Dict, List, Optional

import anthropic
from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
from gtts import gTTS
from pydub import AudioSegment

from . import config
from .emotion_analyzer import EmotionAnalyzer
from .gesture_controller import GestureController
from .voice_animator import VoiceAnimator

logger = logging.getLogger("ConversationManager")

class ConversationManager:
    """Perfect: Normal speed voice, synchronized movements."""
    
    def __init__(self, reachy_mini, claude_api_key: str, nvidia_api_key: Optional[str] = None):
        self.mini = reachy_mini
        self.emotion_analyzer = EmotionAnalyzer(nvidia_api_key, simulation_mode=config.SIMULATION_MODE)
        self.gesture_controller = GestureController(reachy_mini)
        self.voice_animator = VoiceAnimator(reachy_mini)
        self.claude = anthropic.Anthropic(api_key=claude_api_key)
        logger.info(f"Loading Whisper {config.WHISPER_MODEL}...")
        self.whisper = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
        logger.info("✅ TTS: gTTS")
        self.history: List[Dict] = []
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.SYSTEM_PROMPT = (
            "You are Reachy Mini, an empathetic robot. "
            "SHORT answers (1-2 sentences). Warm, curious, helpful. "
            "NEVER describe actions. Speak naturally."
        )

    async def listen_to_user(self, timeout=15) -> Optional[str]:
        """Ultra-sensitive speech detection."""
        logger.info("🎤 SPEAK NOW!")
        threshold, silence_duration, chunk_size = 0.001, 2.5, 2048
        frames, silent_chunks, has_voice, max_vol = [], 0, False, 0.0
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()

        def callback(indata, frame_count, time_info, status):
            if status: logger.warning(f"Audio: {status}")
            loop.call_soon_threadsafe(queue.put_nowait, indata.copy())

        try:
            stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16',
                                   callback=callback, device=config.AUDIO_INPUT_DEVICE, blocksize=chunk_size)
        except Exception as e:
            logger.error(f"❌ Mic: {e}")
            return None
        
        with stream:
            start, count = time.time(), 0
            while True:
                if time.time() - start > timeout:
                    logger.warning(f"⏱️ Timeout (max: {max_vol:.5f})")
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=0.5)
                    frames.append(data)
                    count += 1
                    if len(data) > 0:
                        rms = float(np.sqrt(np.mean((data.astype(np.float32)/32767)**2)))
                        max_vol = max(max_vol, rms)
                        if count % 5 == 0: logger.info(f"Vol: {rms:.5f}")
                    else:
                        rms = 0.0
                    if rms > threshold:
                        silent_chunks, has_voice = 0, True
                    elif has_voice:
                        silent_chunks += 1
                    if has_voice and silent_chunks * (chunk_size / self.sample_rate) > silence_duration:
                        logger.info(f"✅ Speech (max: {max_vol:.5f})")
                        break
                except asyncio.TimeoutError:
                    if has_voice: break
                    continue

        if not has_voice:
            logger.error(f"❌ NO SPEECH (max: {max_vol:.5f})")
            return None

        logger.info(f"📝 Transcribing...")
        temp_path = tempfile.mktemp(suffix=".wav")
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(np.concatenate(frames).tobytes())

        try:
            segments, _ = await asyncio.to_thread(self.whisper.transcribe, temp_path, language="en")
            text = " ".join([s.text for s in segments]).strip()
            if text:
                logger.info(f"✅ '{text}'")
                return text
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)

    async def get_claude_response(self, user_text: str) -> str:
        """Query Claude."""
        messages = [{"role": m["role"], "content": m["content"]} 
                   for m in self.history[-config.MAX_CONVERSATION_HISTORY:]]
        messages.append({"role": "user", "content": user_text})
        try:
            response = await asyncio.to_thread(
                self.claude.messages.create, model="claude-sonnet-4-20250514",
                max_tokens=150, system=self.SYSTEM_PROMPT, messages=messages)
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude: {e}")
            return "Having trouble thinking. Try again?"

    async def speak_response(self, text: str) -> None:
        """FIXED: Normal speed robotic voice, perfect sync."""
        logger.info(f"🔊 {text}")
        try:
            tts = gTTS(text=text, lang="en", slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio = AudioSegment.from_file(fp, format="mp3")
            
            # Robotic but NORMAL SPEED
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * 0.95)})
            audio = audio.set_frame_rate(audio.frame_rate)
            audio = audio.compress_dynamic_range(-15, 3).high_pass_filter(250).normalize()
            
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2)).mean(axis=1)
            samples = samples.astype(np.float32) / 32768.0
            duration = len(samples) / audio.frame_rate
            
            # Perfect sync
            animation_task = asyncio.create_task(self.voice_animator.animate_speech(duration))
            sd.default.blocksize = 4096
            sd.play(samples, audio.frame_rate, blocking=True)
            await animation_task
        except Exception as e:
            logger.error(f"TTS: {e}")
        finally:
            sd.default.blocksize = 0

    async def process_turn(self, user_text: str) -> None:
        """Full turn."""
        if not user_text: return
        self.history.append({"role": "user", "content": user_text})
        response = await self.get_claude_response(user_text)
        self.history.append({"role": "assistant", "content": response})
        emotion = self.emotion_analyzer.analyze(response)
        logger.info(f"🎭 {emotion}")
        await asyncio.gather(
            asyncio.to_thread(self.gesture_controller.perform_gesture, emotion),
            self.speak_response(response))

    def clear_history(self):
        self.history = []
        logger.info("🧹 Cleared")