"""CLI tool for RapidAI."""

import click
from rich.console import Console

from .new import new_command
from .dev import dev_command
from .deploy import deploy_command

console = Console()

__version__ = "0.1.0"


@click.group()
@click.version_option(version=__version__, prog_name="rapidai")
def cli() -> None:
    """RapidAI - The Python framework for lightning-fast AI prototypes."""
    pass


@cli.command("new")
@click.argument("project_name")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["chatbot", "rag", "agent", "api"], case_sensitive=False),
    default="chatbot",
    help="Project template to use",
)
@click.option(
    "--directory",
    "-d",
    type=click.Path(),
    default=".",
    help="Directory to create project in",
)
def new(project_name: str, template: str, directory: str) -> None:
    """Create a new RapidAI project from a template.

    PROJECT_NAME: Name of the project to create
    """
    new_command(project_name, template, directory)


@cli.command("dev")
@click.option(
    "--port",
    "-p",
    type=int,
    default=8000,
    help="Port to run the development server on",
)
@click.option(
    "--host",
    "-h",
    type=str,
    default="127.0.0.1",
    help="Host to bind the development server to",
)
@click.option(
    "--reload/--no-reload",
    default=True,
    help="Enable/disable auto-reload on file changes",
)
@click.option(
    "--app",
    "-a",
    type=str,
    default="app:app",
    help="Application module path (default: app:app)",
)
def dev(port: int, host: str, reload: bool, app: str) -> None:
    """Run the development server with hot reload."""
    dev_command(port=port, host=host, reload=reload, app=app)


@cli.command("deploy")
@click.argument("platform", type=click.Choice(["fly", "heroku", "vercel", "aws"], case_sensitive=False))
@click.option(
    "--app-name",
    "-n",
    type=str,
    help="Application name for deployment",
)
@click.option(
    "--region",
    "-r",
    type=str,
    help="Region to deploy to",
)
def deploy(platform: str, app_name: str | None, region: str | None) -> None:
    """Deploy your RapidAI application to a cloud platform.

    PLATFORM: Cloud platform to deploy to (fly, heroku, vercel, aws)
    """
    deploy_command(platform=platform, app_name=app_name, region=region)


@cli.command("test")
@click.option(
    "--coverage/--no-coverage",
    default=True,
    help="Run with coverage reporting",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
def test(coverage: bool, verbose: bool) -> None:
    """Run tests for your RapidAI application."""
    import subprocess
    import sys

    cmd = ["pytest"]
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        console.print("[red]Error: pytest not found. Install with:[/red]")
        console.print("  pip install pytest pytest-cov")
        sys.exit(1)


@cli.command("docs")
@click.option(
    "--serve/--build",
    default=True,
    help="Serve docs locally or build for production",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=8001,
    help="Port to serve docs on",
)
def docs(serve: bool, port: int) -> None:
    """Generate and serve project documentation."""
    import subprocess
    import sys
    from pathlib import Path

    docs_dir = Path("docs")
    if not docs_dir.exists():
        console.print("[yellow]No docs directory found. Creating basic structure...[/yellow]")
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "index.md").write_text("# Project Documentation\n\nWelcome to the documentation!")

    if serve:
        console.print(f"[green]Serving documentation at http://localhost:{port}[/green]")
        console.print("Press Ctrl+C to stop")
        try:
            subprocess.run(["mkdocs", "serve", "-a", f"localhost:{port}"], check=False)
        except FileNotFoundError:
            console.print("[red]Error: mkdocs not found. Install with:[/red]")
            console.print("  pip install mkdocs mkdocs-material")
            sys.exit(1)
    else:
        console.print("[green]Building documentation...[/green]")
        try:
            subprocess.run(["mkdocs", "build"], check=True)
            console.print("[green]✓ Documentation built successfully in site/[/green]")
        except FileNotFoundError:
            console.print("[red]Error: mkdocs not found. Install with:[/red]")
            console.print("  pip install mkdocs mkdocs-material")
            sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
