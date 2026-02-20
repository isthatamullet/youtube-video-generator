import os
import time
from google import genai

# Load API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key and os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY"):
                api_key = line.split("=")[1].strip()

if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client = genai.Client(api_key=api_key)
video_path = "why_the_ocean_is_salty.mp4"

print(f"Uploading {video_path}...")
video_file = client.files.upload(file=video_path)

print("Waiting for video processing to complete...")
while True:
    video_file = client.files.get(name=video_file.name)
    if video_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
    elif video_file.state.name == "FAILED":
        print("\nVideo processing failed.")
        exit(1)
    else:
        print("\nVideo processing complete.")
        break

print("Requesting review from Gemini...")
response = client.models.generate_content(
    model='gemini-2.5-pro',
    contents=[
        video_file,
        "Please review this generated YouTube Short video. Provide feedback on the narrative pacing, visual relevance (is it accurate/fitting for the topic?), subtitle readability and synchronization, and voiceover quality. Finally, provide actionable suggestions for how to improve the script, assets, or editing."
    ]
)

print("\n=== Gemini Video Review ===")
print(response.text)
