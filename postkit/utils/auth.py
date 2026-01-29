import yaml
from pathlib import Path
import os

def load_credentials(config_path: Path) -> dict:
    """
    Load credentials from YAML config
    Environment variables override config file
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
    
    # Override with env vars
    if 'atproto' in config:
        if os.getenv('ATPROTO_HANDLE'):
            config['atproto']['handle'] = os.getenv('ATPROTO_HANDLE')
        if os.getenv('ATPROTO_PASSWORD'):
            config['atproto']['password'] = os.getenv('ATPROTO_PASSWORD')
    
    if 'substack' in config:
        if os.getenv('SMTP_USER'):
            config['substack']['smtp_user'] = os.getenv('SMTP_USER')
        if os.getenv('SMTP_PASSWORD'):
            config['substack']['smtp_password'] = os.getenv('SMTP_PASSWORD')
    
    return config