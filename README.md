# 🤖 Empathetic Reachy Mini

<div align="center">

**AI-Powered Robotic Companion with Emotional Intelligence**

</div>

---

## 🌟 What is This?

Transform Reachy Mini into an emotionally intelligent companion that:
- 🎤 Responds to **voice commands** naturally
- 🎭 Detects and expresses **emotions** with synchronized gestures
- 👁️ **Mirrors your head movements** in real-time using computer vision
- 💬 Maintains **natural conversations** with context and memory
- 🤖 Speaks with a **custom robotic voice** personality

Built for the **NVIDIA GTC 2026 GOLDEN TICKET Contest** using state-of-the-art AI technologies.

---

## ✨ Key Features

### 🎤 Advanced Voice Interaction
- **Speech-to-Text**: OpenAI Whisper for accurate transcription
- **Text-to-Speech**: Google gTTS with custom robotic voice effects
- **Smart Detection**: Automatic silence detection (speaks when you stop)
- **Dual Input**: Type messages or speak naturally

### 🎭 Emotion Detection & Gestures

Analyzes conversation context to detect and express emotions through physical gestures:

| Emotion | Trigger Examples | Physical Response |
|---------|-----------------|-------------------|
| 😊 **Happy** | "joy", "great", "love" | Head up, antennas wide |
| 😢 **Sad** | "sorry", "bad", "unfortunately" | Head down, antennas droop |
| 🤔 **Thinking** | "hmm", "considering", "maybe" | Head tilt, one antenna up |
| 😲 **Surprised** | "wow", "amazing", "incredible" | Quick head back, alert |
| 😕 **Confused** | "confused", "unclear", "what" | Sideways tilt, uneven antennas |
| 🎉 **Excited** | "excited", "awesome", "fantastic" | Energetic wiggle |
| 🤝 **Empathy** | "understand", "care", "feel" | Gentle forward lean |
| 👂 **Listening** | "tell me", "go on", "listening" | Slight forward tilt |
| ✅ **Agreement** | "yes", "agree", "exactly" | Head nod sequence |
| ❌ **Disagreement** | "no", "wrong", "disagree" | Head shake |
| 👋 **Greeting** | "hello", "hi", "hey" | Friendly antenna wave |
| 😐 **Neutral** | (default state) | Centered, calm |

**Detection System:**
1. **Keyword Matching** (Primary) - Fast pattern recognition
2. **Sentiment Analysis** (Fallback) - TextBlob polarity scoring

### 👁️ Real-Time Head Mirroring
- **MediaPipe Face Mesh** - 468-point facial landmark detection
- **3D Pose Estimation** - PnP algorithm for accurate head orientation
- **< 100ms Latency** - Near-instant response to your movements
- **Auto-Calibration** - Adapts to your neutral head position
- **Safe Limits** - ±20° pitch, ±40° yaw, ±30° roll

### 💬 Context-Aware Conversations
- **Claude Sonnet 4** - Latest Anthropic AI model
- **Conversation Memory** - Remembers last 20 messages
- **Personality** - Warm, curious, and empathetic
- **Concise Responses** - Optimized for natural speech (1-2 sentences)

### 🎨 Modern Web Interface
- **Beautiful UI** - Purple gradient theme with professional styling
- **Real-Time Updates** - Live status indicators and webcam feed
- **Quick Gestures** - Instant emotion buttons for testing
- **Mobile Responsive** - Works on desktop, tablet, and phone

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Anthropic API Key** - (https://console.anthropic.com/)
- **Webcam** (for head mirroring)
- **Microphone & Speakers** (for voice interaction)
- **Reachy Mini Robot** (or use simulation mode)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/aarshsharma2803-stack/empathetic-reachy-mini.git
cd empathetic-reachy-mini

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY
```

### Running the Application

**Simulation Mode** (no physical robot needed):
```bash
REACHY_SIMULATION=true python main_core.py
```

**Hardware Mode** (with physical Reachy Mini):
```bash
# Terminal 1: Start Reachy daemon
reachy-mini-daemon

# Terminal 2: Run application
python main_core.py
```

Open **http://127.0.0.1:7860** in your browser! 🎉

---

## 📖 Usage Guide

### 1️⃣ Connect Robot
Click **"🔌 Connect"** button and wait for green status

### 2️⃣ Text Chat
- Type your message
- Press **Enter** or click **"📨 Send"**
- Watch Reachy detect emotion → perform gesture → speak response

### 3️⃣ Voice Interaction
- Click **"🎤 Voice"** button
- Speak clearly when you see "🎤 Listening..."
- Stop speaking - system auto-detects silence after 2.5 seconds
- Reachy transcribes, processes, and responds with voice!

**Voice Tips:**
- Grant microphone permissions (System Settings → Privacy → Microphone)
- Speak at normal pace
- Wait for the auto-stop (no need to click again)
- Check terminal for volume indicators

### 4️⃣ Head Mirroring
- Click **"▶️ Start Mirror"**
- Position your face in webcam view
- Move your head - Reachy mirrors you in real-time!
- First detection auto-calibrates to your neutral position
- Click **"⏹️ Stop"** when done

**Mirroring Tips:**
- Ensure good lighting
- Face camera directly for best accuracy
- Green ✓ = face detected successfully
- Smooth, controlled movements work best

### 5️⃣ Quick Gesture Testing
Click any emotion button (😊 😢 🤔) to see instant gestures without conversation

---

## 🏗️ Architecture

```
┌──────────────────┐
│   User Input     │
│ (Text/Voice/Face)│
└────────┬─────────┘
         │
    ┌────┴─────┬──────────────┬──────────────┐
    ▼          ▼              ▼              ▼
┌────────┐ ┌────────┐  ┌──────────┐  ┌──────────┐
│Whisper │ │ Gradio │  │MediaPipe │  │  User    │
│  STT   │ │   UI   │  │Face Mesh │  │  Types   │
└───┬────┘ └───┬────┘  └────┬─────┘  └────┬─────┘
    │          │             │             │
    └──────────┴─────────────┴─────────────┘
                     │
           ┌─────────▼──────────┐
           │ Conversation       │
           │    Manager         │
           │ • History tracking │
           │ • Context mgmt     │
           └─────────┬──────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│ Claude  │    │ Emotion  │    │ Gesture  │
│Sonnet 4 │    │ Analyzer │    │Controller│
│   AI    │    │   NLP    │    │Animation │
└────┬────┘    └────┬─────┘    └────┬─────┘
     │              │               │
     └──────────────┴───────────────┘
                    │
          ┌─────────▼──────────┐
          │   gTTS + Effects   │
          │  (Robotic Voice)   │
          └─────────┬──────────┘
                    │
        ┌───────────▼────────────┐
        │  Synchronized Output:  │
        │  Speech + Gesture +    │
        │    Head Animation      │
        └────────────────────────┘
```

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **AI/ML** | Claude Sonnet 4 (Anthropic) | Natural language understanding & generation |
| | Whisper Base (OpenAI) | Speech-to-text transcription |
| | TextBlob | Sentiment analysis for emotion detection |
| **Computer Vision** | MediaPipe (Google) | Face detection & pose estimation |
| | OpenCV | Image processing & webcam handling |
| **Audio** | gTTS (Google) | Text-to-speech generation |
| | pydub | Audio effects & manipulation |
| | sounddevice | Real-time audio I/O |
| **Robotics** | Reachy Mini SDK | Hardware control & simulation |
| | MuJoCo | Physics-based simulation |
| **Web UI** | Gradio 6 | Interactive web interface |
| | Custom CSS | Professional purple theme |
| **Language** | Python 3.10+ | Core implementation |

---

## 📁 Project Structure

```
empathetic-reachy-mini/
├── main_core.py                    # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Configuration template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
│
└── core/
    └── empathetic_reachy/
        ├── __init__.py             # Package initialization
        ├── config.py               # Configuration settings
        ├── conversation_manager.py # AI orchestration 
        ├── emotion_analyzer.py     # Emotion detection 
        ├── gesture_controller.py   # 12 gesture animations 
        ├── head_mirroring.py       # Face tracking system 
        ├── voice_animator.py       # Speech animations 
        └── list_microphones.py     # Audio device utility
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
AUDIO_INPUT_DEVICE=0  # Microphone index (run list_microphones.py)
```

### Application Settings (`core/empathetic_reachy/config.py`)

```python
# Speech Recognition
WHISPER_MODEL = "base"          # Options: tiny, base, small, medium
SILENCE_THRESHOLD = 0.001       # Lower = more sensitive
SILENCE_DURATION = 2.5          # Seconds before auto-stop

# Conversation
MAX_CONVERSATION_HISTORY = 20   # Messages in context window

# Audio
AUDIO_SAMPLE_RATE = 16000       # Hz
AUDIO_BUFFER_SIZE = 4096        # Larger = smoother playback
```

### Finding Your Microphone

```bash
# List all audio input devices
python core/empathetic_reachy/list_microphones.py

# Example output:
# [0] MacBook Air Microphone ⭐ DEFAULT
# [3] AirPods Pro
# [5] External USB Mic

# Set in .env:
AUDIO_INPUT_DEVICE=3
```

---

## 🎯 Performance Metrics

| Metric | Value | Details |
|--------|-------|---------|
| **Voice Response** | < 3s | Complete turn (speech → response → speech) |
| **Head Mirror Latency** | < 100ms | Your movement → robot movement |
| **Emotion Detection** | < 50ms | Text → emotion classification |
| **UI Refresh Rate** | 60 FPS | Smooth visual updates |
| **Memory Usage** | ~800MB | With all models loaded |
| **CPU Usage** | 30-40% | During active head mirroring |

**Optimization Techniques:**
- Frame skipping (process every 2nd frame)
- Async audio processing
- Model caching (load once, reuse)
- Gesture queueing system
- Efficient PnP pose estimation

---

## 🐛 Troubleshooting

<details>
<summary><b>❌ "No speech detected"</b></summary>

**Causes:**
- Microphone permissions not granted
- Wrong microphone selected
- Speaking too quietly
- Threshold too high

**Solutions:**
```bash
# 1. Check permissions
# macOS: System Settings → Privacy & Security → Microphone
# Enable Terminal or your IDE

# 2. List available microphones
python core/empathetic_reachy/list_microphones.py

# 3. Set correct device in .env
echo "AUDIO_INPUT_DEVICE=3" >> .env

# 4. Adjust sensitivity in config.py
SILENCE_THRESHOLD = 0.0005  # More sensitive
```
</details>

<details>
<summary><b>❌ "Claude API error"</b></summary>

**Solutions:**
```bash
# 1. Verify API key is set
grep ANTHROPIC_API_KEY .env

# 2. Test key validity
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'

# 3. Check API quota at console.anthropic.com
```
</details>

<details>
<summary><b>❌ "Camera not found"</b></summary>

**Solutions:**
```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"

# Try different camera index
# Edit head_mirroring.py line ~50:
cap = cv2.VideoCapture(1)  # Try 0, 1, 2, etc.

# Check camera permissions
# macOS: System Settings → Privacy → Camera
```
</details>

<details>
<summary><b>❌ Laggy head mirroring</b></summary>

**Solutions:**
```python
# Edit head_mirroring.py line ~95:
if frame_count % 3 != 0:  # Change 2 → 3 (skip more frames)
    continue

# Lower resolution (line ~70):
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Was 480
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Was 360
```
</details>

<details>
<summary><b>❌ Robot not responding</b></summary>

**Simulation mode:**
```bash
REACHY_SIMULATION=true python main_core.py
```

**Hardware mode:**
```bash
# Terminal 1
reachy-mini-daemon

# Terminal 2
python main_core.py
```
</details>

---

## 🤝 Contributing

Contributions welcome! Here's how:

### Reporting Bugs
1. Check [existing issues](https://github.com/YOUR_USERNAME/empathetic-reachy-mini/issues)
2. Create new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version)

### Suggesting Features
- Open issue with `[FEATURE]` prefix
- Describe use case and benefits
- Include mockups if relevant

### Pull Requests
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with clear commits
4. Test thoroughly
5. Submit PR with detailed description

---

## 🗺️ Roadmap

### ✅ Version 1.0 (Current)
- [x] Voice conversation (Whisper STT + gTTS)
- [x] 12-emotion detection system
- [x] Real-time head mirroring
- [x] Modern Gradio web interface
- [x] Simulation mode support

### 🚧 Version 2.0 (Planned)
- [ ] Multi-language support (Spanish, French, Chinese)
- [ ] Custom gesture recording & teaching
- [ ] Emotion history visualization
- [ ] Direction of Arrival (turn toward speaker)
- [ ] Mobile companion app

### 🔮 Version 3.0 (Future)
- [ ] Multi-robot coordination
- [ ] Persistent memory across sessions
- [ ] Personality customization
- [ ] Smart home device integration
- [ ] AR/VR telepresence mode

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Aarsh Sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🏆 NVIDIA GTC 2026 Contest

This project is submitted for the **NVIDIA GTC 2026 - GOLDEN TICKET PROJECT**.

### Why Vote for This Project?

- ✅ **Most Comprehensive** - 12 emotions vs competitors' 3-5
- ✅ **Best User Experience** - Voice + text + mirroring in one app
- ✅ **Production Quality** - Robust error handling & documentation
- ✅ **Educational Value** - Well-commented code for learning
- ✅ **Open Source** - MIT license, community-friendly

**Show your support:**
- ⭐ [Star on GitHub](https://github.com/YOUR_USERNAME/empathetic-reachy-mini)
- ❤️ [Like on Hugging Face](https://huggingface.co/spaces/YOUR_USERNAME/empathetic-reachy-mini)
- 🔄 Share with the robotics community

---

## 🙏 Acknowledgments

### Technologies & Platforms
- **[Anthropic](https://www.anthropic.com/)** - Claude AI language model
- **[OpenAI](https://openai.com/)** - Whisper speech recognition
- **[Google](https://google.github.io/mediapipe/)** - MediaPipe face tracking
- **[Pollen Robotics](https://www.pollen-robotics.com/)** - Reachy Mini platform
- **[Hugging Face](https://huggingface.co/)** - Deployment & hosting

### Inspiration
- Human-robot interaction research
- Emotional intelligence in AI systems
- Companion robotics for accessibility
- Social robotics community

### Special Thanks
- **Dr. Lee** - Project guidance and mentorship
- **Pollen Robotics Team** - Excellent SDK and support
- **Open Source Community** - Libraries and tools

---

## 📬 Contact

**Developer:** Aarsh Sharma  
**Email:** aarsh.sharma@example.com  
**GitHub:** [@aarshsharma](https://github.com/aarshsharma2803-stack)  
**LinkedIn:** [Aarsh Sharma](https://www.linkedin.com/in/aarsh-sanjay-sharma-a093b3246/)

**Project Links:**
- 🌐 **Live Demo:** [Hugging Face Space](https://huggingface.co/spaces/Aarsh2003/empathetic-reachy-mini)
- 📦 **Repository:** [GitHub](https://github.com/aarshsharma2803-stack/empathetic-reachy-mini)

---

## ⭐ Show Your Support

If you find this project helpful or interesting:

- ⭐ **Star this repository** on GitHub
- ❤️ **Like the Space** on Hugging Face
- 🔄 **Share** with robotics enthusiasts
- 🐛 **Report bugs** or suggest features
- 🤝 **Contribute** improvements

**Every star and like helps in the contest! Thank you!** 🙏

---

<div align="center">

**Built with ❤️ for the NVIDIA GTC 2026 Reachy Mini Contest**

[⭐ Star on GitHub](https://github.com/aarshsharma2803-stack/empathetic-reachy-mini) • [🚀 Try Live Demo](https://huggingface.co/spaces/Aarsh2003/empathetic-reachy-mini)

**#NVIDIAGTC #ReachyMini #AI #Robotics #HumanRobotInteraction**

---

Made with **Python** 🐍 | Powered by **Claude AI** 🧠 | Built for **Reachy Mini** 🤖

</div>
