import os
import json
from dotenv import load_dotenv

# Project root is one level up from src/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(_PROJECT_ROOT, '.env'))

def load_config():
    config_path = os.path.join(_PROJECT_ROOT, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_env_var(key):
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Environment variable {key} not set. Please check your .env file.")
    return val
