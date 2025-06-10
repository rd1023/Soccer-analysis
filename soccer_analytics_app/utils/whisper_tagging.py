# Mock Whisper voice-to-tag system
def detect_voice_tags(audio_path):
    # In reality, run Whisper on audio to extract events
    return [
        {"Event Type": "Shot", "Timestamp": 45, "Player": "11", "Location": "210,140", "Notes": "Called: Shot by 11"}
    ]
