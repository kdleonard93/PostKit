from pathlib import Path
from typing import Dict, Any, Optional
import re

def normalize_for_platforms(
    post_data: Dict[str, Any],
    image_path: Optional[Path] = None,
    video_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Transform content for each platform
    
    Takes the parsed markdown and creates platform-specific versions:
    - AT Protocol (Bluesky/Flashes/Pinksky): Threads and summaries
    - Substack: Full HTML email
    
    Returns:
    {
        'atproto': {
            'thread': ['chunk1', 'chunk2', ...],
            'summary': 'Brief summary',
            'hashtags': ['#tech', '#python'],
            'image': Path(...),
        },
        'substack': {
            'title': 'My Post',
            'html': '<html>...</html>',
            'subject': 'My Post',
        }
    }
    """
    content = post_data['content']
    title = post_data['title']
    short = post_data.get('short', '')
    tags = post_data.get('tags', [])
    html = post_data['html']
    
    # Create thread chunks (for Bluesky/Pinksky)
    thread_chunks = create_thread_chunks(content, title, max_length=280)
    
    # Create summary (for Flashes)
    if short:
        # Use the 'short' from frontmatter if provided
        summary = short
    else:
        # Extract first paragraph as summary
        first_para = extract_first_paragraph(content)
        summary = truncate_text(first_para, 280)
    
    # Add title to summary if it's not already there
    if title.lower() not in summary.lower():
        summary = f"{title}\n\n{summary}"
        summary = truncate_text(summary, 280)
    
    # Format hashtags
    hashtags = [f"#{tag.strip().replace(' ', '')}" for tag in tags]
        
    # Build HTML email for Substack
    email_html = build_substack_email(title, html, image_path)
    
    return {
        'atproto': {
            'thread': thread_chunks,
            'summary': summary,
            'hashtags': hashtags,
            'image': image_path,
            'video': video_path,
            'title': title
        },
        'substack': {
            'title': title,
            'html': email_html,
            'subject': title,
            'tags': tags
        }
    }

    
def extract_first_paragraph(content: str) -> str:
    """
    Get the first paragraph from markdown content
    Used for creating summaries
    """
    # Remove any frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    # Remove headers (lines starting with #)
    content = re.sub(r'^#+\s+.+$', '', content, flags=re.MULTILINE)
    
    # Split by blank lines and get first non-empty paragraph
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    return paragraphs[0] if paragraphs else ''


def truncate_text(text: str, max_length: int, ellipsis: str = '...') -> str:
    """
    Cut text to max_length, adding ... at the end
    """
    if len(text) <= max_length:
        return text
    
    cutoff = text.rfind(' ', 0, max_length - len(ellipsis))
    if cutoff == -1:
        cutoff = max_length - len(ellipsis)
    
    return text[:cutoff] + ellipsis


def create_thread_chunks(content, title, max_length=280):
    """
    Smart chunking strategy:
    
    1. First chunk: Title + opening paragraph
    2. Split remaining by paragraphs (double newline)
    3. If paragraph > max_length, split by sentences
    4. Add thread numbering: "(1/5)", "(2/5)", etc.
    5. Attach image to first chunk only
    
    Example output:
    [
        "My Great Post\n\nThis is the opening...\n\n(1/5)",
        "Second paragraph content here...\n\n(2/5)",
        ...
    ]
    """
    chunks = []
    
    # Clean content (remove markdown headers)
    clean_content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
    
    # First chunk: title + first paragraph
    if paragraphs:
        first_chunk = f"{title}\n\n{paragraphs[0]}"
        if len(first_chunk) <= max_length:
            chunks.append(first_chunk)
            remaining = paragraphs[1:]
        else:
            chunks.append(truncate_text(title, max_length))
            remaining = paragraphs
    
    # Process remaining paragraphs
    current_chunk = ""
    for para in remaining:
        test_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
        
        if len(test_chunk) <= max_length:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            # If paragraph itself is too long, split by sentences
            if len(para) > max_length:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                temp = ""
                for sentence in sentences:
                    if len(temp) + len(sentence) + 1 <= max_length:
                        temp = f"{temp} {sentence}".strip()
                    else:
                        if temp:
                            chunks.append(temp)
                        temp = sentence
                current_chunk = temp
            else:
                current_chunk = para
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Add thread numbering
    total = len(chunks)
    if total > 1:
        chunks = [f"{chunk}\n\n({i+1}/{total})" for i, chunk in enumerate(chunks)]
    
    return chunks

def build_substack_email(title, html_content, image_path):
    """
    Create beautiful HTML email:
    - Proper DOCTYPE and meta tags
    - Inline CSS for styling
    - Embedded cover image (if provided)
    - Responsive design
    """
    template = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 680px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 { font-size: 2em; margin-bottom: 0.5em; }
            h2 { font-size: 1.5em; margin-top: 1.5em; }
            img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {cover_image}
        {content}
    </body>
    </html>"""
    
    cover_image_html = '<img src="cid:cover_image">' if image_path else ''
    
    return template.format(
        title=title,
        cover_image=cover_image_html,
        content=html_content
    )