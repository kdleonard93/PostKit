import yaml
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def load_credentials(config_path: Path) -> dict:
    """
    Load credentials from YAML config
    Environment variables override config file
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
    
    # Override with env vars - AT Protocol
    if 'atproto' in config:
        if os.getenv('ATPROTO_HANDLE'):
            config['atproto']['handle'] = os.getenv('ATPROTO_HANDLE')
        if os.getenv('ATPROTO_PASSWORD'):
            config['atproto']['password'] = os.getenv('ATPROTO_PASSWORD')
    
    # Override with env vars - Substack
    if 'substack' in config:
        if os.getenv('SMTP_USER'):
            config['substack']['smtp_user'] = os.getenv('SMTP_USER')
        if os.getenv('SMTP_PASSWORD'):
            config['substack']['smtp_password'] = os.getenv('SMTP_PASSWORD')

        if os.getenv('SUBSTACK_EMAIL'):
            config['substack']['email'] = os.getenv('SUBSTACK_EMAIL')
        if os.getenv('SMTP_HOST'):
            config['substack']['smtp_host'] = os.getenv('SMTP_HOST')
        if os.getenv('SMTP_PORT'):
            config['substack']['smtp_port'] = int(os.getenv('SMTP_PORT'))
    
    return config