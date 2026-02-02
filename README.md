# PostKit

Multi-platform publishing tool that lets you write once and publish everywhere. Support for AT Protocol (Bluesky, Flashes, Pinksky, Skylight) and Substack with more platforms coming soon.

## Features

- **Multi-platform publishing** - Write once, publish to multiple platforms simultaneously
- **Smart content normalization** - Automatically formats content for each platform's requirements
- **Thread support** - Long posts are automatically split into threaded conversations
- **Media attachments** - Support for images and videos
- **Hashtag handling** - Automatic hashtag formatting for platform-specific requirements
- **Dry run mode** - Preview what will be published before actually posting
- **Rich CLI** - Beautiful command-line interface with progress indicators

## Supported Platforms

- **AT Protocol** (Bluesky, Flashes, Pinksky, Skylight)
- **Substack** (via email)
- More platforms coming soon...

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-username/postkit.git
cd postkit

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Configuration

### 1. Initialize Configuration

```bash
postkit init
```

This creates a `config.example.yaml` file with the structure you need.

### 2. Set Up Your Credentials

Copy the example file and add your actual credentials:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` with your platform credentials:

```yaml
atproto:
  handle: your-handle.bsky.social
  password: your-app-password  # Use app password, not regular password

substack:
  email: publication@substack.com
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_user: you@gmail.com
  smtp_password: your-app-password  # Use app password
```

### Platform-Specific Setup

#### AT Protocol (Bluesky, etc.)

1. Go to [Bluesky Settings](https://bsky.app/settings)
2. Navigate to "Privacy & Security" → "App Passwords"
3. Create a new app password
4. Use your handle (e.g., `username.bsky.social`) and app password in config

#### Substack

1. Set up your Substack publication email (usually `publication@substack.com`)
2. Create an app password for your email provider (Gmail recommended)
3. Configure SMTP settings in config.yaml

## Usage

### Basic Publishing

```bash
# Publish a markdown file
postkit publish path/to/your-post.md

# Include an image
postkit publish post.md --image path/to/image.jpg

# Include a video
postkit publish post.md --video path/to/video.mp4

# Dry run to preview what will be published
postkit publish post.md --dry-run
```

### Content Format

Create markdown files with frontmatter:

```markdown
---
title: Your Post Title
short: Brief summary for platforms
tags: tech, python, tutorial
---

# Your Content Here

Your main content goes here. This will be automatically formatted for each platform.
```

#### Frontmatter Fields

- `title` (optional) - Post title, defaults to first H1 if not specified
- `short` (optional) - Brief summary for platforms with character limits
- `tags` (optional) - Comma-separated list of hashtags

### How It Works

1. **Content Parsing** - Reads your markdown file and extracts metadata
2. **Normalization** - Formats content for each platform's requirements:
   - AT Protocol: Splits long content into threaded posts (300 char limit)
   - Substack: Sends as HTML email
3. **Publishing** - Posts to all configured platforms simultaneously
4. **Reporting** - Shows success/failure status for each platform

## Examples

### Short Post
```bash
postkit publish short-post.md
```
Creates a single post on AT Protocol and email to Substack.

### Long Post
```bash
postkit publish long-post.md
```
Automatically splits into threaded conversation on AT Protocol, full email to Substack.

### Post with Media
```bash
postkit publish post.md --image cover.jpg
```
Includes image in the first post of the thread.

## Development

### Project Structure

```
postkit/
├── postkit/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── formats/
│   │   ├── __init__.py
│   │   ├── markdown.py     # Markdown parsing
│   │   └── normalizer.py   # Content normalization
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── atproto.py      # AT Protocol publisher
│   │   └── substack.py     # Substack publisher
│   └── utils/
│       ├── __init__.py
│       └── auth.py         # Credential management
├── tests/                  # Test files
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
└── README.md              # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest

# Run with coverage
pytest --cov=postkit
```

### Adding New Platforms

1. Create a new publisher in `postkit/platforms/`
2. Implement the `publish` method
3. Add platform configuration to config template
4. Update the normalizer to handle platform-specific formatting

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Open a pull request

## Troubleshooting

### Common Issues

**Authentication Errors**
- Ensure you're using app passwords, not regular passwords
- Check that your handle includes the domain (e.g., `username.bsky.social`)
- Verify SMTP settings for Substack

**Content Not Posting**
- Use `--dry-run` to preview what will be published
- Check that your config.yaml is properly formatted
- Ensure all required credentials are present

**Thread Issues**
- Long posts are automatically split at sentence boundaries
- Each chunk respects platform character limits
- Images are only attached to the first post in a thread

### Debug Mode

Set environment variable for verbose logging:

```bash
export POSTKIT_DEBUG=1
postkit publish post.md
```

## Configuration Reference

### Complete config.yaml

```yaml
atproto:
  handle: your-handle.bsky.social
  password: your-app-password

substack:
  email: publication@substack.com
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_user: you@gmail.com
  smtp_password: your-app-password
```

### Environment Variables

As an alternative to config.yaml, you can use environment variables:

```bash
export ATPROTO_HANDLE=your-handle.bsky.social
export ATPROTO_PASSWORD=your-app-password
export SMTP_USER=you@gmail.com
export SMTP_PASSWORD=your-app-password
export SUBSTACK_HANDLE=publication@substack.com
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- AT Protocol support (Bluesky, Flashes, Pinksky, Skylight)
- Substack email support
- Markdown parsing with frontmatter
- Thread splitting for long content
- Image attachment support
- Dry run mode

## Support

- **Issues**: [GitHub Issues](https://github.com/kdleonard93/PostKit/issues)

## Roadmap

- [ ] Mastodon support
- [ ] LinkedIn integration
- [ ] Twitter/X support
- [ ] Content scheduling
- [ ] Template system
- [ ] Analytics dashboard
- [ ] Web interface

---

Made with ❤️ for content creators who want to focus on writing, not platform management.
