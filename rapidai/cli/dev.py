"""Development server command for RapidAI CLI."""

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def dev_command(port: int, host: str, reload: bool, app: str) -> None:
    """Run the development server with hot reload.

    Args:
        port: Port to run server on
        host: Host to bind to
        reload: Enable auto-reload
        app: Application module path
    """
    # Check if app file exists
    app_file = app.split(":")[0].replace(".", "/") + ".py"
    if not Path(app_file).exists():
        console.print(f"[red]Error: Application file not found: {app_file}[/red]")
        console.print("[yellow]Make sure you're in the project directory or specify --app[/yellow]")
        console.print()
        console.print("[cyan]Example:[/cyan]")
        console.print("  rapidai dev --app myapp:app")
        return

    # Display startup message
    console.print()
    console.print(Panel.fit(
        f"[green]🚀 RapidAI Development Server[/green]\n\n"
        f"[cyan]Application:[/cyan] {app}\n"
        f"[cyan]URL:[/cyan] http://{host}:{port}\n"
        f"[cyan]Hot reload:[/cyan] {'Enabled' if reload else 'Disabled'}\n\n"
        f"[yellow]Press Ctrl+C to stop[/yellow]",
        border_style="cyan"
    ))
    console.print()

    # Build uvicorn command
    cmd = [
        "uvicorn",
        app,
        "--host", host,
        "--port", str(port),
    ]

    if reload:
        cmd.extend([
            "--reload",
            "--reload-exclude", "*.pyc",
            "--reload-exclude", "__pycache__",
            "--reload-exclude", ".git",
        ])

    # Run uvicorn
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        console.print("\n[yellow]Development server stopped[/yellow]")
    except FileNotFoundError:
        console.print("[red]Error: uvicorn not found. Install with:[/red]")
        console.print("  pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error running server: {e}[/red]")
        sys.exit(1)
