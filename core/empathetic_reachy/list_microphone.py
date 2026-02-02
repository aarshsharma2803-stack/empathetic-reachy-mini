#!/usr/bin/env python3
"""
List all available audio input devices.
Run this to find your microphone device number.
"""

import sounddevice as sd # type: ignore

print("=" * 60)
print("🎤 AVAILABLE AUDIO INPUT DEVICES")
print("=" * 60)

devices = sd.query_devices()

input_devices = []
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        input_devices.append((i, device))
        print(f"\n[{i}] {device['name']}")
        print(f"    Channels: {device['max_input_channels']}")
        print(f"    Sample Rate: {device['default_samplerate']} Hz")
        if i == sd.default.device[0]:
            print(f"    ⭐ CURRENTLY DEFAULT")

print("\n" + "=" * 60)
print("\n💡 HOW TO USE:")
print("   1. Find your device number from the list above")
print("   2. Edit config.py:")
print("      AUDIO_INPUT_DEVICE = <device_number>")
print("   3. Restart the app")
print("\n📝 EXAMPLE:")
print("   If your Bluetooth headset is device [3]:")
print("   AUDIO_INPUT_DEVICE = 3")
print("=" * 60)