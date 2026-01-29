import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

app = typer.Typer(name="postkit", help="Multi-platform publishing")
console = Console()

@app.command()
def publish(
    content_path: Path = typer.Argument(..., help="Markdown file"),
    image: Path = typer.Option(None, "--image"),
    video: Path = typer.Option(None, "--video"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Publish content to all platforms"""
    
    # Validate files
    if not content_path.exists():
        console.print(f"[red]✗[/red] File not found: {content_path}")
        raise typer.Exit(1)
    
    # Load credentials
    from .utils.auth import load_credentials
    creds = load_credentials(Path("config.yaml"))
    
    # Parse content
    from .formats.markdown import parse_markdown_post
    post_data = parse_markdown_post(content_path)
    
    # Normalize
    from .formats.normalizer import normalize_for_platforms
    normalized = normalize_for_platforms(post_data, image, video)
    
    # Dry run preview
    if dry_run:
        console.print("\n[bold cyan]📋 Dry Run Preview[/bold cyan]\n")
        console.print(f"Title: {post_data['title']}")
        console.print(f"Platforms: Bluesky, Flashes, Pinksky, Substack")
        return
    
    # Publish
    console.print("\n[bold cyan]🚀 Publishing...[/bold cyan]\n")
    
    results = {'success': [], 'failed': []}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # AT Protocol
        if 'atproto' in creds:
            task = progress.add_task("Publishing to AT Protocol...", total=None)
            try:
                from .platforms.atproto import ATProtoPublisher
                pub = ATProtoPublisher(creds['atproto'])
                at_results = pub.publish(normalized['atproto'])
                
                for platform, success in at_results.items():
                    if success:
                        results['success'].append(platform)
                        console.print(f"[green]✓[/green] {platform}")
                    else:
                        results['failed'].append(platform)
                        console.print(f"[red]✗[/red] {platform}")
            except Exception as e:
                console.print(f"[red]✗[/red] AT Protocol error: {e}")
                results['failed'].extend(['Bluesky', 'Flashes', 'Pinksky'])
            finally:
                progress.update(task, completed=True)
        
        # Substack
        if 'substack' in creds:
            task = progress.add_task("Publishing to Substack...", total=None)
            try:
                from .platforms.substack import SubstackPublisher
                pub = SubstackPublisher(creds['substack'])
                success = pub.publish(normalized['substack'])
                
                if success:
                    results['success'].append('Substack')
                    console.print(f"[green]✓[/green] Substack")
                else:
                    results['failed'].append('Substack')
            except Exception as e:
                console.print(f"[red]✗[/red] Substack error: {e}")
                results['failed'].append('Substack')
            finally:
                progress.update(task, completed=True)
    
    # Summary
    console.print(f"\n[bold]📊 Summary[/bold]")
    console.print(f"✓ Success: {len(results['success'])}")
    console.print(f"✗ Failed: {len(results['failed'])}\n")
    
    if results['failed']:
        raise typer.Exit(1)

@app.command()
def init():
    """Initialize config file"""
    import yaml
    
    example = {
        'atproto': {
            'handle': 'your-handle.bsky.social',
            'password': 'your-app-password'
        },
        'substack': {
            'email': 'publication@substack.com',
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'you@gmail.com',
            'smtp_password': 'your-app-password'
        }
    }
    
    with open('config.example.yaml', 'w') as f:
        yaml.dump(example, f)
    
    console.print("[green]✓[/green] Created config.example.yaml")
    console.print("\nNext: Copy to config.yaml and add your credentials")

def main():
    app()