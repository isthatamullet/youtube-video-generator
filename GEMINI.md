# YouTube Video Generator — AI Context

This file provides context for AI assistants working on this project.

## Architecture

The pipeline has two phases:

**Local (Antigravity/CLI):**
- `main.py` → interactive prompts → Gemini script generation → Colab notebook export → Drive upload

**Remote (Google Colab):**
- The generated `.ipynb` runs the full render pipeline on Colab's T4 GPU:
  Cell 1: Install deps (ffmpeg-python, edge-tts, whisper)
  Cell 2: Inject config, scenes, API keys
  Cell 3: Generate voiceover (Edge-TTS) + timestamps (Whisper)
  Cell 4: Fetch Pexels B-roll videos
  Cell 5: Render scene previews (ffmpeg filter graphs + ASS subtitles) → interactive carousel
  Cell 6: Scene swap tool (re-fetch + re-render single scene)
  Cell 7: Final stitch (ffmpeg concat, no re-encoding)
  Cell 8: Export to Google Drive

## Key Design Decisions

- **FFmpeg over MoviePy**: MoviePy was ~40 min for a 60s video due to Python-level frame processing. FFmpeg renders in ~2 min using native C code.
- **ASS subtitles**: Words are grouped into 4-word phrases and burned via FFmpeg's `ass` filter. Style: bottom-center, Liberation Sans bold, white with black outline.
- **Scene-by-scene workflow**: Each scene renders independently for review before final stitch. The final stitch uses `c='copy'` (stream copy, no re-encoding).
- **Colab for GPU**: Free T4 GPU handles Whisper transcription. FFmpeg runs on CPU but is fast enough.

## Config (config.json)

Key settings:
- `video_settings.resolution`: [1920, 1080] or [1080, 1920]
- `video_settings.fps`: 30
- `audio_and_voice.voice_model`: Edge-TTS voice ID
- `visuals_and_subtitles.font_size`: ASS subtitle font size

## Module Map

- `src/colab_builder.py` — The core notebook generator. Most changes happen here.
- `src/script_generator.py` — Gemini prompt engineering for scene scripts.
- `src/drive_uploader.py` — Uses Google Drive API v3 with ADC auth.
- `src/utils.py` — `_PROJECT_ROOT` resolves paths relative to repo root.

## Known Patterns

- All notebook cell code is stored as Python list-of-strings in `colab_builder.py`
- Special characters in cell strings need careful escaping (quotes, backslashes)
- The `render_scene_preview()` function defined in Cell 5 is reused by Cell 6 (scene swap)
- Pexels API: 200 req/hour, 20K/month free tier — no concern at current usage

## Pending Ideas

- Toggleable captions via SRT/VTT export alongside burned-in subs
- Background music tracks with audio ducking
- Canva MCP for thumbnail generation and infographic overlays
- Colab VS Code extension for direct runtime access from Antigravity
