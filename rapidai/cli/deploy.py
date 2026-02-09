"""Deployment command for RapidAI CLI."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


def generate_fly_config(app_name: str, region: Optional[str] = None) -> str:
    """Generate fly.toml configuration.

    Args:
        app_name: Application name
        region: Region to deploy to

    Returns:
        fly.toml content
    """
    region_line = f'primary_region = "{region}"' if region else ""

    return f'''# fly.toml
app = "{app_name}"
{region_line}

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80
    force_https = true

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.http_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health"
'''


def generate_procfile() -> str:
    """Generate Procfile for Heroku."""
    return '''web: uvicorn app:app --host 0.0.0.0 --port $PORT
'''


def generate_vercel_config() -> str:
    """Generate vercel.json configuration."""
    return '''{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
'''


def deploy_fly(app_name: Optional[str], region: Optional[str]) -> None:
    """Deploy to Fly.io.

    Args:
        app_name: Application name
        region: Region to deploy to
    """
    console.print("[cyan]Deploying to Fly.io...[/cyan]")
    console.print()

    # Check if flyctl is installed
    try:
        subprocess.run(["flyctl", "version"], capture_output=True, check=True)
    except FileNotFoundError:
        console.print("[red]Error: flyctl not found. Install from https://fly.io/docs/hands-on/install-flyctl/[/red]")
        return

    # Determine app name
    if not app_name:
        app_name = Prompt.ask("Enter app name", default="rapidai-app")

    # Check if fly.toml exists
    if not Path("fly.toml").exists():
        console.print("[yellow]No fly.toml found. Generating...[/yellow]")
        fly_config = generate_fly_config(app_name, region)
        Path("fly.toml").write_text(fly_config)
        console.print("[green]✓ Created fly.toml[/green]")

    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        console.print("[yellow]Warning: No requirements.txt found[/yellow]")
        if not Confirm.ask("Continue anyway?"):
            return

    # Launch or deploy
    console.print()
    console.print("[cyan]Running: flyctl deploy[/cyan]")
    result = subprocess.run(["flyctl", "deploy"], check=False)

    if result.returncode == 0:
        console.print()
        console.print(Panel.fit(
            f"[green]✓ Deployed successfully![/green]\n\n"
            f"[cyan]URL:[/cyan] https://{app_name}.fly.dev\n"
            f"[cyan]Dashboard:[/cyan] https://fly.io/apps/{app_name}",
            title="🚀 Fly.io Deployment",
            border_style="green"
        ))
    else:
        console.print("[red]Deployment failed. Check the output above for errors.[/red]")


def deploy_heroku(app_name: Optional[str], region: Optional[str]) -> None:
    """Deploy to Heroku.

    Args:
        app_name: Application name
        region: Region to deploy to
    """
    console.print("[cyan]Deploying to Heroku...[/cyan]")
    console.print()

    # Check if heroku CLI is installed
    try:
        subprocess.run(["heroku", "version"], capture_output=True, check=True)
    except FileNotFoundError:
        console.print("[red]Error: heroku CLI not found. Install from https://devcenter.heroku.com/articles/heroku-cli[/red]")
        return

    # Determine app name
    if not app_name:
        app_name = Prompt.ask("Enter app name", default="rapidai-app")

    # Check if Procfile exists
    if not Path("Procfile").exists():
        console.print("[yellow]No Procfile found. Generating...[/yellow]")
        Path("Procfile").write_text(generate_procfile())
        console.print("[green]✓ Created Procfile[/green]")

    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        console.print("[red]Error: requirements.txt not found[/red]")
        return

    # Create app if it doesn't exist
    console.print(f"[cyan]Creating Heroku app: {app_name}[/cyan]")
    region_flag = ["--region", region] if region else []
    subprocess.run(["heroku", "create", app_name] + region_flag, check=False)

    # Set buildpack
    subprocess.run(["heroku", "buildpacks:set", "heroku/python", "-a", app_name], check=False)

    # Deploy
    console.print()
    console.print("[cyan]Deploying via git push...[/cyan]")
    console.print("[yellow]Make sure you've committed your changes and added heroku remote![/yellow]")
    console.print()
    console.print("[cyan]Commands to run:[/cyan]")
    console.print(f"  git remote add heroku https://git.heroku.com/{app_name}.git")
    console.print("  git push heroku main")


def deploy_vercel(app_name: Optional[str], region: Optional[str]) -> None:
    """Deploy to Vercel.

    Args:
        app_name: Application name
        region: Region to deploy to
    """
    console.print("[cyan]Deploying to Vercel...[/cyan]")
    console.print()

    # Check if vercel CLI is installed
    try:
        subprocess.run(["vercel", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        console.print("[red]Error: vercel CLI not found. Install with:[/red]")
        console.print("  npm install -g vercel")
        return

    # Check if vercel.json exists
    if not Path("vercel.json").exists():
        console.print("[yellow]No vercel.json found. Generating...[/yellow]")
        Path("vercel.json").write_text(generate_vercel_config())
        console.print("[green]✓ Created vercel.json[/green]")

    # Deploy
    console.print()
    console.print("[cyan]Running: vercel --prod[/cyan]")
    name_flag = ["--name", app_name] if app_name else []
    result = subprocess.run(["vercel", "--prod"] + name_flag, check=False)

    if result.returncode == 0:
        console.print()
        console.print(Panel.fit(
            "[green]✓ Deployed successfully![/green]\n\n"
            "[cyan]Check the output above for your deployment URL[/cyan]",
            title="🚀 Vercel Deployment",
            border_style="green"
        ))


def deploy_aws(app_name: Optional[str], region: Optional[str]) -> None:
    """Deploy to AWS (placeholder).

    Args:
        app_name: Application name
        region: Region to deploy to
    """
    console.print("[cyan]AWS Deployment[/cyan]")
    console.print()
    console.print("[yellow]AWS deployment is a manual process. Here's what you need to do:[/yellow]")
    console.print()
    console.print("[cyan]1. Package your application:[/cyan]")
    console.print("   - Create requirements.txt")
    console.print("   - Set up application.py for AWS Lambda or ECS")
    console.print()
    console.print("[cyan]2. Choose a deployment method:[/cyan]")
    console.print("   - AWS Lambda + API Gateway (serverless)")
    console.print("   - AWS ECS/Fargate (containers)")
    console.print("   - AWS Elastic Beanstalk (platform)")
    console.print()
    console.print("[cyan]3. Use AWS CLI or Console:[/cyan]")
    console.print("   - Install AWS CLI: https://aws.amazon.com/cli/")
    console.print("   - Configure credentials: aws configure")
    console.print("   - Deploy using chosen method")
    console.print()
    console.print("[cyan]Recommended: Use AWS SAM or CDK for infrastructure as code[/cyan]")


def deploy_command(platform: str, app_name: Optional[str], region: Optional[str]) -> None:
    """Deploy application to a cloud platform.

    Args:
        platform: Cloud platform to deploy to
        app_name: Application name
        region: Region to deploy to
    """
    deployers = {
        "fly": deploy_fly,
        "heroku": deploy_heroku,
        "vercel": deploy_vercel,
        "aws": deploy_aws,
    }

    deployer = deployers.get(platform)
    if deployer:
        deployer(app_name, region)
    else:
        console.print(f"[red]Unknown platform: {platform}[/red]")
