from pathlib import Path
from typing import Dict, Any

def parse_markdown_post(file_path: Path) -> Dict[str, Any]:
    """
    Parse markdown content with frontmatter
    
    Input:
    ---
    title: My Post
    short: Brief summary
    tags: tech, python
    ---
    # Content here
    
    Output:
    {
        'title': 'My Post',
        'short': 'Brief summary',
        'tags': ['tech', 'python'],
        'content': '# Content here',
        'html': '<h1>Content here</h1>'
    }
    """