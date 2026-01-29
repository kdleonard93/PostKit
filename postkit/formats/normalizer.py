from pathlib import Path
from typing import Dict, Any
import re

def normalize_for_platforms(post_data, image_path, video_path) -> Dict[str, Any]:
    """
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