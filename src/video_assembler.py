import os
import json
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from .utils import load_config
import textwrap

def generate_video(script_scenes: list, voiceover_path: str, b_roll_paths: list[str], word_timestamps: list[dict], output_path: str):
    """Combines B-roll, voiceover, and text into a final video using MoviePy."""
    config = load_config()
    
    # 1. Video Settings
    target_res = tuple(config['video_settings']['resolution'])
    fps = config['video_settings']['fps']
    
    # 2. Setup Audio
    if not os.path.exists(voiceover_path):
        raise FileNotFoundError(f"Voiceover not found: {voiceover_path}")
    audio_clip = AudioFileClip(voiceover_path)
    total_duration = audio_clip.duration
    
    # 3. Assemble B-roll Clips
    if not b_roll_paths:
        raise ValueError("No B-roll videos provided.")
    
    video_clips = []
    current_time = 0
    b_roll_idx = 0
    b_roll_duration = config['pacing_and_editing']['b_roll_duration_seconds']
    
    while current_time < total_duration:
        b_roll_file = b_roll_paths[b_roll_idx % len(b_roll_paths)]
        if not os.path.exists(b_roll_file):
            raise FileNotFoundError(f"B-roll not found: {b_roll_file}")
            
        clip = VideoFileClip(b_roll_file)
        
        # Determine clip duration
        clip_duration = min(b_roll_duration, total_duration - current_time)
        clip = clip.subclipped(0, min(clip.duration, clip_duration))
        
        # Crop and resize to fill target_res completely (whether portrait or landscape)
        target_w, target_h = target_res
        clip_ratio = clip.w / clip.h
        target_ratio = target_w / target_h
        
        if clip_ratio > target_ratio:
            # Clip is wider than target. Scale height to match target_h, crop width.
            clip = clip.resized(height=target_h)
            clip = clip.cropped(x_center=clip.w / 2, y_center=clip.h / 2, width=target_w, height=target_h)
        else:
            # Clip is taller than target. Scale width to match target_w, crop height.
            clip = clip.resized(width=target_w)
            clip = clip.cropped(x_center=clip.w / 2, y_center=clip.h / 2, width=target_w, height=target_h)
        
        # Optionally handle transition type from config if duration > transition... here we just append
        
        video_clips.append(clip)
        current_time += clip.duration
        b_roll_idx += 1
        
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video = final_video.with_audio(audio_clip)
    
    # 4. Burn in Subtitles
    # Group words into chunks and overlay
    text_clips = []
    
    max_words = config['visuals_and_subtitles']['max_words_per_line']
    font_size = config['visuals_and_subtitles']['font_size']
    font = config['visuals_and_subtitles']['font_family']
    color = "white" # defaulting to generic colors for MoviePy textclip
    stroke_color = "black"
    stroke_width = 2
    
    # Simple chunking for subtitles
    for word in word_timestamps:
        txt_clip = TextClip(
            font=font,
            text=word['word'],
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method="caption",
            size=(target_res[0] - 100, None)
        )
        # Position in center
        txt_clip = txt_clip.with_position(('center', 'center'))
        txt_clip = txt_clip.with_start(word['start'])
        txt_clip = txt_clip.with_end(word['end'])
        
        text_clips.append(txt_clip)
        
    # Combine everything
    composite = CompositeVideoClip([final_video] + text_clips)
    
    # 5. Render
    print(f"Rendering final video to {output_path}...")
    composite.write_videofile(
        output_path, 
        fps=fps, 
        codec="libx264", 
        audio_codec="aac",
        threads=4
    )
    print("Video generation complete.")
