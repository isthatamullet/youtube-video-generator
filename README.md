# YouTube Video Generator

An automated YouTube video generation pipeline that creates videos from a text topic using AI-powered scripting, text-to-speech, stock footage, and subtitle synchronization.

## How It Works

```
Topic → AI Script → Voiceover → B-Roll → Subtitles → Rendered Video
```

1. **`main.py`** prompts for a topic, format (vertical/horizontal), and duration
2. **Gemini 2.5 Pro** generates a structured script with scenes and visual queries
3. A **Google Colab notebook** is generated containing the full rendering pipeline:
   - **Edge-TTS** generates the voiceover
   - **Whisper** transcribes word-level timestamps for subtitle sync
   - **Pexels** fetches matching stock footage for each scene
   - **FFmpeg** assembles everything (scale, crop, subtitle burn, audio mix)
4. The notebook is uploaded to **Google Drive** and opened in Colab
5. Scene previews are rendered individually with an **interactive carousel** for review
6. Approved scenes are stitched into the final video and exported to Drive

## Setup

```bash
# Clone and enter the project
git clone https://github.com/yourusername/youtube-video-generator.git
cd youtube-video-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install google-genai pydantic inquirer python-dotenv edge-tts \
            openai-whisper ffmpeg-python requests google-auth \
            google-api-python-client

# Configure API keys
cp .env.example .env
# Edit .env with your keys
```

### Required API Keys

| Key | Source | Purpose |
|-----|--------|---------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) | Script generation |
| `PEXELS_API_KEY` | [Pexels](https://www.pexels.com/api/) | Stock video footage |

### Google Drive API

The Drive uploader uses Application Default Credentials. Run:
```bash
gcloud auth application-default login
```

## Usage

```bash
python main.py
```

Follow the interactive prompts to:
1. Enter a video topic
2. Choose format (vertical shorts or horizontal)
3. Set target duration
4. Review/edit the generated script
5. Generate and upload the Colab notebook

Then open the Colab link, select a **T4 GPU runtime**, and run all cells.

## Project Structure

```
├── main.py              # Entry point — interactive CLI
├── config.json          # Video settings (resolution, voice, pacing)
├── .env                 # API keys (gitignored)
├── src/
│   ├── script_generator.py   # Gemini script generation
│   ├── colab_builder.py      # Generates .ipynb notebooks
│   ├── drive_uploader.py     # Google Drive sync
│   ├── voiceover_gen.py      # Edge-TTS wrapper
│   ├── subtitle_sync.py      # Whisper transcription
│   ├── visuals_fetcher.py    # Pexels video search
│   ├── video_assembler.py    # FFmpeg video assembly
│   ├── review.py             # Script review helper
│   └── utils.py              # Config loading, env vars
└── projects/                 # Generated output (gitignored)
```

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Script AI | Gemini 2.5 Pro | Free tier |
| Voice | Edge-TTS | Free |
| Subtitles | OpenAI Whisper | Free |
| B-Roll | Pexels API | Free |
| Video Engine | FFmpeg | Free |
| GPU Runtime | Google Colab | Free tier |
| Storage | Google Drive | Free |

## Roadmap

- [ ] Toggleable captions (SRT/VTT export for YouTube)
- [ ] Background music with auto-ducking
- [ ] Canva integration for thumbnails and title cards
- [ ] Longer-form content (5-15 min documentaries)
- [ ] Section title cards and chapter markers
- [ ] Colab VS Code extension for direct runtime access
