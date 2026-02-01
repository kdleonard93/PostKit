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
    
    thread_chunks = create_thread_chunks(content, title, max_length=300)
    
    if short:
        summary = short
    else:
        first_para = extract_first_paragraph(content)
        summary = truncate_text(first_para, 280)
    
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


def create_thread_chunks(content, title, max_length=300):
    """
    Smart chunking strategy with reserved space for thread numbering
    
    Strategy:
    1. Make initial chunks with conservative limit
    2. Calculate suffix length based on total chunks
    3. Re-chunk if needed to ensure all fit within max_length
    """
    
    # Helper function to do the actual chunking
    def chunk_content(effective_max_length):
        chunks = []
        
        clean_content = content
        clean_content = re.sub(r'^#\s+.+$', '', clean_content, flags=re.MULTILINE)
        clean_content = re.sub(r'^##\s+(.+)$', r'▸ \1', clean_content, flags=re.MULTILINE)
        clean_content = re.sub(r'^###\s+(.+)$', r'• \1', clean_content, flags=re.MULTILINE)
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
        paragraphs = [p for p in paragraphs if p]
        
        # First chunk: Title + first paragraph
        if paragraphs:
            first_chunk = f"{title}\n\n{paragraphs[0]}"
            if len(first_chunk) <= effective_max_length:
                chunks.append(first_chunk)
                remaining = paragraphs[1:]
            else:
                # Title alone
                chunks.append(truncate_text(title, effective_max_length))
                remaining = paragraphs
        else:
            chunks.append(truncate_text(title, effective_max_length))
            remaining = []
        
        # Process remaining paragraphs
        current_chunk = ""
        for para in remaining:
            test_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            
            if len(test_chunk) <= effective_max_length:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                if len(para) > effective_max_length:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        test_sentence = f"{temp_chunk} {sentence}".strip() if temp_chunk else sentence
                        
                        if len(test_sentence) <= effective_max_length:
                            temp_chunk = test_sentence
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            
                            if len(sentence) <= effective_max_length:
                                temp_chunk = sentence
                            else:
                                # Split long sentence into word-based chunks
                                words = sentence.split()
                                word_chunk = ""
                                
                                for word in words:
                                    test_word_chunk = f"{word_chunk} {word}".strip() if word_chunk else word
                                    
                                    if len(test_word_chunk) <= effective_max_length:
                                        word_chunk = test_word_chunk
                                    else:
                                        if word_chunk:
                                            chunks.append(word_chunk)
                                        word_chunk = word
                                
                                temp_chunk = word_chunk
                    
                    current_chunk = temp_chunk
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    # Initial chunking with conservative estimate
    # Assume max 2-digit numbering: "\n\n(99/99)" = 10 chars
    initial_reserved = 10
    chunks = chunk_content(max_length - initial_reserved)
    
    total = len(chunks)
    if total > 1:
        suffix_length = len(f"\n\n({total}/{total})")
        
        if suffix_length != initial_reserved:
            chunks = chunk_content(max_length - suffix_length)
            total = len(chunks)
            
            new_suffix_length = len(f"\n\n({total}/{total})")
            
            iteration_count = 0
            while new_suffix_length != suffix_length and iteration_count < 5:
                suffix_length = new_suffix_length
                chunks = chunk_content(max_length - suffix_length)
                total = len(chunks)
                new_suffix_length = len(f"\n\n({total}/{total})")
                iteration_count += 1
        
        chunks = [f"{chunk}\n\n({i+1}/{total})" for i, chunk in enumerate(chunks)]
        
        chunks = [
            chunk if len(chunk) <= max_length else truncate_text(chunk, max_length)
            for chunk in chunks
        ]
    
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
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 680px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{ font-size: 2em; margin-bottom: 0.5em; }}
            h2 {{ font-size: 1.5em; margin-top: 1.5em; }}
            img {{ max-width: 100%; height: auto; }}
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