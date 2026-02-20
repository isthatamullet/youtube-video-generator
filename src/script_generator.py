import os
import json
from pydantic import BaseModel
from google import genai
from .utils import load_config, get_env_var

class Scene(BaseModel):
    text: str
    visual_query: str

class Script(BaseModel):
    scenes: list[Scene]

def generate_script(topic: str) -> list[dict]:
    """Generates a structured script using Gemini 3.1 Pro via the google-genai library."""
    print(f"Generating script for topic: '{topic}'...")
    
    config = load_config()
    system_prompt = config['prompts']['script_generation_system_prompt']
    
    api_key = get_env_var("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # We ask Gemini to generate the output conforming to our Pydantic schema
    response = client.models.generate_content(
        model='gemini-3.1-pro-preview',
        contents=f"{system_prompt}\n\nTopic: {topic}",
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Script,
            temperature=0.7
        )
    )
    
    try:
        script_data = json.loads(response.text)
        print(f"Successfully generated a script with {len(script_data.get('scenes', []))} scenes.")
        return script_data['scenes']
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        print("Raw response:", response.text)
        raise

if __name__ == "__main__":
    # Test the generator if run directly
    test_topic = "The Fall of the Roman Empire"
    try:
        scenes = generate_script(test_topic)
        print(json.dumps(scenes, indent=2))
    except Exception as e:
        print(f"Script generation failed: {e}")
