import gradio as gr
import asyncio
import logging
import time
import threading
import cv2
import numpy as np
from reachy_mini import ReachyMini
from core.empathetic_reachy import config
from core.empathetic_reachy.conversation_manager import ConversationManager
from core.empathetic_reachy.head_mirroring import HeadMirroringController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReachyUI")

class ReachyOracle:
    def __init__(self):
        self.mini = None
        self.manager = None
        self.mirror_controller = None
        self.sim_status = "🔴 Disconnected"
        self.is_mirroring = False
        self.current_frame = None
        self.mirror_thread = None

    def initialize_robot(self):
        try:
            logger.info("Connecting...")
            self.mini = ReachyMini(connection_mode='localhost_only') if config.SIMULATION_MODE else ReachyMini()
            self.manager = ConversationManager(self.mini, config.ANTHROPIC_API_KEY, config.NVIDIA_API_KEY)
            self.mirror_controller = HeadMirroringController(self.mini)
            self.sim_status = "🟢 Connected (Sim)" if config.SIMULATION_MODE else "🟢 Connected"
            return self.sim_status
        except Exception as e:
            return f"🔴 Error: {str(e)}"

    async def chat_interaction(self, user_input, history):
        if not user_input.strip():
            yield history, self.sim_status, "neutral"
            return
        if not self.manager:
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": "⚠️ Not connected"})
            yield history, "⚠️ Not connected", "neutral"
            return
            
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": "🤔..."})
        yield history, "🤔 Thinking", "neutral"
        
        self.manager.history.append({"role": "user", "content": user_input})
        try:
            response = await self.manager.get_claude_response(user_input)
            self.manager.history.append({"role": "assistant", "content": response})
            emotion = self.manager.emotion_analyzer.analyze(response)
            
            history[-1] = {"role": "assistant", "content": response}
            yield history, f"🎭 {emotion}", emotion
            
            await asyncio.to_thread(self.manager.gesture_controller.perform_gesture, emotion)
            yield history, "🗣️ Speaking", emotion
            await self.manager.speak_response(response)
            yield history, "✅ Ready", emotion
        except Exception as e:
            logger.error(f"Error: {e}")
            history[-1] = {"role": "assistant", "content": f"❌ {str(e)}"}
            yield history, "🔴 Error", "sad"

    async def voice_interaction(self, history):
        if not self.manager:
            yield history, "❌ Not connected", "neutral"
            return
        yield history, "🎤 Listening...", "neutral"
        user_text = await self.manager.listen_to_user()
        if not user_text:
            yield history, "❌ No speech", "neutral"
            return
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": "🤔..."})
        yield history, "🤔 Processing", "neutral"
        async for h, s, e in self.chat_interaction(user_text, history[:-2]):
            yield h, s, e

    def perform_quick_gesture(self, emotion):
        if self.manager:
            try:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(self.manager.gesture_controller.perform_gesture, emotion).result(timeout=5)
                return f"✅ {emotion}"
            except Exception as e:
                return f"❌ {e}"
        return "⚠️ Not connected"

    def clear_memory(self):
        if self.manager: self.manager.clear_history()
        return [], "🧹 Cleared"

    def _mirror_loop(self):
        if not self.mirror_controller: return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.is_mirroring = False
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv2.CAP_PROP_FPS, 30)
        logger.info("Webcam started")
        frame_count = 0
        
        while self.is_mirroring and cap.isOpened():
            frame_count += 1
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            if frame_count % 2 != 0:
                time.sleep(0.005)
                continue
            
            image = cv2.flip(frame, 1)
            img_h, img_w = image.shape[:2]
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.mirror_controller.face_mesh.process(image_rgb)
            
            if results.multi_face_landmarks:
                face = results.multi_face_landmarks[0]
                pose = self.mirror_controller.calculate_head_pose(face, img_w, img_h)
                if not self.mirror_controller.calibrated:
                    self.mirror_controller.pitch_offset = pose['pitch']
                    self.mirror_controller.yaw_offset = pose['yaw']
                    self.mirror_controller.roll_offset = pose['roll']
                    self.mirror_controller.calibrated = True
                self.mirror_controller.mirror_to_reachy(pose)
                cv2.putText(image, "✓", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(image, "✗", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            self.current_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            time.sleep(0.015)
        
        cap.release()
        self.is_mirroring = False

    def start_mirroring(self):
        if self.is_mirroring: return "⚠️ Already on"
        if not self.mirror_controller: return "❌ Connect first"
        self.is_mirroring = True
        self.mirror_controller.calibrated = False
        self.mirror_thread = threading.Thread(target=self._mirror_loop, daemon=True)
        self.mirror_thread.start()
        return "▶️ Started"

    def stop_mirroring(self):
        self.is_mirroring = False
        self.current_frame = None
        return "⏹️ Stopped"

    def get_current_frame(self):
        return self.current_frame if self.current_frame is not None else np.zeros((360, 480, 3), dtype=np.uint8)

oracle = ReachyOracle()

# PERFECT CSS
css = """
.main-title {
    text-align: center;
    font-size: 2.5em;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 20px 0;
}
.subtitle {
    text-align: center;
    color: #666;
    font-size: 1.1em;
    margin-bottom: 30px;
}
.big-button {
    min-height: 50px !important;
    font-size: 1.1em !important;
}
.gesture-btn {
    min-height: 60px !important;
    font-size: 1.3em !important;
}
"""

with gr.Blocks(title="Reachy Mini AI") as demo:
    gr.HTML('<div class="main-title">🤖 Empathetic Reachy Mini</div>')
    gr.HTML('<div class="subtitle">AI-Powered Robot with Voice, Emotion & Gestures</div>')
    
    # CONNECTION
    with gr.Row():
        status_box = gr.Textbox(value="🔴 Disconnected", label="Status", scale=3, interactive=False)
        connect_btn = gr.Button("🔌 Connect", variant="primary", scale=1, elem_classes="big-button")
    
    # MAIN LAYOUT
    with gr.Row(equal_height=True):
        # LEFT: Vision & Gestures
        with gr.Column(scale=1):
            gr.Markdown("### 📷 Live Vision")
            camera_view = gr.Image(label="Webcam", height=300)
            
            with gr.Row():
                mirror_btn = gr.Button("▶️ Start Mirror", variant="primary", elem_classes="big-button")
                stop_btn = gr.Button("⏹️ Stop", variant="stop", elem_classes="big-button")
            
            mirror_status = gr.Textbox(value="⏸️ Not mirroring", label="Mirror Status")
            emotion_display = gr.Label(label="🎭 Emotion", value="neutral")
            
            gr.Markdown("### 🎨 Quick Gestures")
            with gr.Row():
                gr.Button("😊", elem_classes="gesture-btn").click(
                    fn=lambda: oracle.perform_quick_gesture("happy"), outputs=gr.Textbox(visible=False))
                gr.Button("😢", elem_classes="gesture-btn").click(
                    fn=lambda: oracle.perform_quick_gesture("sad"), outputs=gr.Textbox(visible=False))
                gr.Button("🤔", elem_classes="gesture-btn").click(
                    fn=lambda: oracle.perform_quick_gesture("thinking"), outputs=gr.Textbox(visible=False))
        
        # RIGHT: Chat
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Conversation")
            chatbot = gr.Chatbot(height=500)
            msg_box = gr.Textbox(label="Message", placeholder="Type or click Voice...", lines=2)
            
            with gr.Row():
                send_btn = gr.Button("📨 Send", variant="primary", scale=2, elem_classes="big-button")
                voice_btn = gr.Button("🎤 Voice", variant="secondary", scale=2, elem_classes="big-button")
                clear_btn = gr.Button("🗑️", variant="stop", scale=1)
    
    status_indicator = gr.Textbox(label="Action", value="💤 Idle")
    
    gr.Markdown("---")
    gr.Markdown("**Features:** Speech-to-Speech • Real-time Emotion Detection • Head Mirroring • Natural Gestures")
    
    # TIMER
    timer = gr.Timer(0.15)
    timer.tick(fn=oracle.get_current_frame, outputs=camera_view)
    
    # EVENTS
    connect_btn.click(fn=oracle.initialize_robot, outputs=status_box)
    mirror_btn.click(fn=oracle.start_mirroring, outputs=mirror_status)
    stop_btn.click(fn=oracle.stop_mirroring, outputs=mirror_status)
    msg_box.submit(fn=oracle.chat_interaction, inputs=[msg_box, chatbot], 
                   outputs=[chatbot, status_indicator, emotion_display]).then(lambda: "", None, msg_box)
    send_btn.click(fn=oracle.chat_interaction, inputs=[msg_box, chatbot], 
                   outputs=[chatbot, status_indicator, emotion_display]).then(lambda: "", None, msg_box)
    voice_btn.click(fn=oracle.voice_interaction, inputs=[chatbot], 
                    outputs=[chatbot, status_indicator, emotion_display])
    clear_btn.click(fn=oracle.clear_memory, outputs=[chatbot, status_indicator])

if __name__ == "__main__":
    config.validate_config()
    config.print_config()
    demo.queue().launch(share=False, theme=gr.themes.Soft(primary_hue="purple"), css=css)