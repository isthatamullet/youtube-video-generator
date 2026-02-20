import os
import asyncio
import edge_tts
from .utils import load_config

def generate_voiceover(text: str, output_filepath: str) -> str:
    """Generates an MP3 voiceover using Edge TTS for the given text."""
    config = load_config()
    voice_model = config['audio_and_voice']['voice_model']
    rate = config['audio_and_voice']['tts_rate']
    pitch = config['audio_and_voice']['tts_pitch']
    
    print(f"Generating voiceover with model {voice_model}...")
    
    communicate = edge_tts.Communicate(text, voice_model, rate=rate, pitch=pitch)
    
    async def save_audio():
        await communicate.save(output_filepath)
        
    asyncio.run(save_audio())
    print(f"Voiceover saved to {output_filepath}")
    return output_filepath

if __name__ == "__main__":
    test_text = "Did you know that the Roman Empire lasted for over a thousand years, before finally falling in 476 AD?"
    out_path = os.path.join(os.path.dirname(__file__), "test_voiceover.mp3")
    try:
        generate_voiceover(test_text, out_path)
    except Exception as e:
        print(f"Voiceover generation failed: {e}")
