import os
import requests
import random
from .utils import get_env_var, load_config

def get_pexels_video(query: str, orientation: str = "portrait", size: str = "medium") -> str:
    """Fetches a free stock video URL from Pexels based on the query."""
    api_key = get_env_var("PEXELS_API_KEY")
    headers = {"Authorization": api_key}
    
    url = f"https://api.pexels.com/videos/search?query={query}&orientation={orientation}&size={size}&per_page=5"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch videos from Pexels: {response.status_code}")
        print(response.text)
        return ""
        
    data = response.json()
    videos = data.get("videos", [])
    
    if not videos:
        print(f"No videos found for query '{query}'")
        return ""
        
    # Select a random video from the top 5 results to add variety
    video = random.choice(videos)
    video_files = video.get("video_files", [])
    
    if not video_files:
        return ""
        
    # Find the link corresponding to the best quality hd or sd
    best_file = None
    for vf in video_files:
        if vf.get("quality") == "hd":
            best_file = vf
            break
            
    if not best_file:
        best_file = video_files[0]
        
    return best_file.get("link", "")

def download_video(url: str, output_path: str) -> bool:
    """Downloads a video from a given URL to the output path."""
    if not url:
        return False
        
    print(f"Downloading video from {url} to {output_path}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Download complete.")
        return True
    else:
        print(f"Failed to download video: {response.status_code}")
        return False

if __name__ == "__main__":
    test_query = "ancient Rome"
    dl_dir = os.path.dirname(__file__)
    out_path = os.path.join(dl_dir, "test_b_roll.mp4")
    
    try:
        video_url = get_pexels_video(test_query)
        if video_url:
            download_video(video_url, out_path)
    except Exception as e:
        print(f"Fetching visuals failed: {e}")
