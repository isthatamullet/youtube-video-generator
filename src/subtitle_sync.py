import os
import whisper

# Load model globally to avoid loading it on every call. "base" keeps it fast.
MODEL = None

def get_word_timestamps(audio_path: str) -> list[dict]:
    """Uses Whisper to transcribe the given audio file and extract word-level timestamps."""
    global MODEL
    if MODEL is None:
        print("Loading Whisper model...")
        MODEL = whisper.load_model("base")
        
    print(f"Transcribing audio from {audio_path}...")
    # Word-level timestamps require word_timestamps=True
    result = MODEL.transcribe(audio_path, word_timestamps=True)
    
    words = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            words.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })
            
    print(f"Transcription complete. Found {len(words)} words.")
    return words

if __name__ == "__main__":
    test_audio = os.path.join(os.path.dirname(__file__), "test_voiceover.mp3")
    if os.path.exists(test_audio):
        try:
            words = get_word_timestamps(test_audio)
            print(words[:5], "...")  # Preview first few words
        except Exception as e:
            print(f"Subtitle syncing failed: {e}")
    else:
        print(f"Test audio not found at {test_audio}. Run voiceover_gen.py first.")
