import os
import json
import inquirer
import re
from src.script_generator import generate_script
from src.colab_builder import create_colab_notebook
from src.drive_uploader import upload_project_folder
from src.utils import load_config, get_env_var

def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters, and converts spaces to hyphens."""
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '_', value)
    return value

def get_user_configuration(config):
    questions = [
        inquirer.Text('topic', message="What is the topic of the YouTube Short?"),
        inquirer.List('format',
                      message="What format should the video be?",
                      choices=['Vertical/Shorts (1080x1920)', 'Horizontal (1920x1080)'],
                      default='Vertical/Shorts (1080x1920)'
        ),
        inquirer.Text('duration', 
                      message="Target duration in seconds (approximate)", 
                      default=str(config['video_settings']['target_duration_seconds']))
    ]
    answers = inquirer.prompt(questions)
    
    if not answers or not answers['topic']:
        print("Setup cancelled or invalid topic. Exiting.")
        return None

    # Update config based on user input
    try:
        config['video_settings']['target_duration_seconds'] = int(answers['duration'])
    except ValueError:
        print("Invalid duration, keeping default.")
        
    if "Vertical" in answers['format']:
        config['video_settings']['resolution'] = [1080, 1920]
    else:
        config['video_settings']['resolution'] = [1920, 1080]
        
    return answers['topic'], config

def run_pipeline():
    print(f"=== YouTube Video Generator ===")
    
    # Load default config
    config = load_config()
    
    # --- Interactive Setup ---
    result = get_user_configuration(config)
    if not result:
        return
    topic, config = result
    
    topic_slug = slugify(topic)
    
    # directories
    base_dir = os.path.dirname(__file__)
    project_dir = os.path.join(base_dir, "projects", topic_slug)
    os.makedirs(project_dir, exist_ok=True)
    
    output_video = os.path.join(project_dir, f"{topic_slug}_final.mp4")
    
    print(f"\n--- Step 1: Generating Script for '{topic}' ---")
    scenes = generate_script(topic)
    if not scenes:
        print("Failed to generate script.")
        return
        
    script_path = os.path.join(project_dir, "script.json")
    with open(script_path, "w") as f:
        json.dump(scenes, f, indent=2)
    print(f"Script saved to {script_path}")
    
    # --- Interactive Review ---
    print(f"\n--- Script Generated! ---")
    print(f"Please open the script file to review and make any edits:")
    print(f"{script_path}")
        
    questions = [
        inquirer.List('action',
                      message="\nWhenever you are ready, how would you like to proceed?",
                      choices=['I have reviewed/edited the script. Generate Video!', 'Cancel Generation'],
                      default='I have reviewed/edited the script. Generate Video!'
        )
    ]
    review = inquirer.prompt(questions)
    if not review or review['action'] != 'I have reviewed/edited the script. Generate Video!':
        print("\nGeneration cancelled. The script has been saved to the project directory.")
        return
        
    # Reload the script from disk in case the user made edits
    try:
        with open(script_path, "r") as f:
            scenes = json.load(f)
    except Exception as e:
        print(f"Error loading edited script: {e}")
        return
    
    # Construct full script text for TTS
    # (We no longer generate TTS locally, it's done in the Colab notebook)
    
    # Reload the config we wrote to disk to make sure we have latest duration
    try:
        config = load_config()
    except Exception:
        pass # fallback to what we already have in memory
    
    print("\n--- Step 2: Generating Colab Video Engine ---")
    notebook_json = create_colab_notebook(
        topic_slug=topic_slug, 
        config=config, 
        scenes=scenes, 
        pexels_api_key=get_env_var('PEXELS_API_KEY')
    )
    
    notebook_path = os.path.join(project_dir, f"{topic_slug}_generator.ipynb")
    with open(notebook_path, "w", encoding='utf-8') as f:
        json.dump(notebook_json, f, indent=2)
    print(f"Notebook saved to {notebook_path}")
    
    # --- Step 3: Upload to Google Drive ---
    print("\n--- Step 3: Uploading Project to Google Drive ---")
    upload_project_folder(project_dir, topic_slug)
    
    print(f"\n=== Process Complete! ===")
    print("Your project folder has been synced to Google Drive.")
    print("Open Google Colab and find your notebook in Drive > youtube-video-generator >")
    print(f"  {topic_slug} > {topic_slug}_generator.ipynb")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nPipeline failed: {e}")
