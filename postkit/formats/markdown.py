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
    
def markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to HTML
    """
    try:
        import markdown
        md = markdown.Markdown(extensions=['extra'])
        return md.convert(markdown_text)
    except:
        return basic_markdown_to_html(markdown_text)
    
def basic_markdown_to_html(text: str) -> str:
    """
    Backup method
    Converts: headers, bold, italic, links
    """
    html = text
    
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    
    paragraphs = html.split('\n\n')
    html = '\n'.join(
        f'<p>{p}</p>' if not p.startswith('<h') else p 
        for p in paragraphs 
        if p.strip()
    )
    
    return html

def truncate_text(text: str, max_length: int, ellipsis: str = '...') -> str:
    """
    Cut text to max_length, adding ... at the end
    Example: truncate_text("Hello world", 8) → "Hello..."
    """
    if len(text) <= max_length:
        return text
    
    # Find last space before the limit (don't cut words in half)
    cutoff = text.rfind(' ', 0, max_length - len(ellipsis))
    if cutoff == -1:
        cutoff = max_length - len(ellipsis)
    
    return text[:cutoff] + ellipsis