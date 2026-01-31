from importlib import metadata
from pathlib import Path
from typing import Dict, Any
import re
import yaml

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
    
    content = file_path.read_text(encoding='utf-8')
    
    frontmatter_match = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_match, content, re.DOTALL)
    
    if match:
        frontmatter_text, body= match.groups()
        metadata = yaml.safe_load(frontmatter_text) or {}
    else:
        metadata = {}
        body = content
        
    title = metadata.get('title')
    if not title:
        h1_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
        else:
            title = "Untitled Post"
    
    tags = metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]
        
    html = markdown_to_html(body)
    
    return {
        'title': title,
        'short': metadata.get('short', ''),
        'tags': tags,
        'content': body.strip(),
        'html': html,
        'metadata': metadata
    }
    