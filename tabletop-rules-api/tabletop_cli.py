#!/usr/bin/env python3
"""
Tabletop Rules CLI - Command Line Interface for Game Rules Management

A comprehensive CLI tool for managing tabletop game rules with the FastAPI backend.
Provides efficient content management for single-admin workflows.

Usage:
    python tabletop_cli.py --help
    python tabletop_cli.py upload rules_data/chess_rules.md
    python tabletop_cli.py list-games
    python tabletop_cli.py validate chess
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="tabletop-cli",
    help="🎲 Tabletop Rules CLI - Manage game rules efficiently",
    rich_markup_mode="rich"
)

console = Console()

class TabletopAPI:
    """HTTP client for FastAPI backend communication."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def authenticate(self, username: str = "admin", password: str = "secret") -> bool:
        """Authenticate with the FastAPI backend."""
        try:
            response = await self.client.post(
                f"{self.base_url}/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                return True
            else:
                console.print(f"[red]Authentication failed: {response.status_code}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]Authentication error: {str(e)}[/red]")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token."""
        if not self.token:
            raise typer.Exit("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    async def upload_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Upload a markdown file to the backend."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "text/markdown")}
            response = await self.client.post(
                f"{self.base_url}/api/admin/upload/markdown-simple",
                files=files,
                headers=self._get_headers()
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    async def list_games(self) -> List[Dict[str, Any]]:
        """List all registered games."""
        response = await self.client.get(
            f"{self.base_url}/api/admin/games/registered",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()["games"]
        else:
            response.raise_for_status()
    
    async def get_game_rules(self, game_id: str) -> List[Dict[str, Any]]:
        """Get rules for a specific game."""
        response = await self.client.get(
            f"{self.base_url}/api/admin/games/{game_id}/rules",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()["rules"]
        else:
            response.raise_for_status()
    
    async def delete_game(self, game_id: str) -> Dict[str, Any]:
        """Delete a game and all its rules."""
        response = await self.client.delete(
            f"{self.base_url}/api/admin/games/{game_id}",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    async def validate_game(self, game_id: str) -> Dict[str, Any]:
        """Validate game rules integrity."""
        response = await self.client.post(
            f"{self.base_url}/api/admin/games/{game_id}/validate",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    async def batch_upload(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Upload multiple files in batch."""
        results = []
        for file_path in file_paths:
            try:
                result = await self.upload_markdown(file_path)
                result["file_path"] = str(file_path)
                results.append(result)
            except Exception as e:
                results.append({
                    "file_path": str(file_path),
                    "success": False,
                    "error": str(e)
                })
        return results
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global API client
api_client = TabletopAPI()

@app.command()
def upload(
    file_path: Path = typer.Argument(..., help="Path to markdown file to upload"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output")
):
    """📄 Upload a markdown rules file to the backend."""
    async def _upload():
        # Authenticate
        with console.status("[bold blue]Authenticating...", spinner="dots"):
            if not await api_client.authenticate():
                raise typer.Exit(1)
        
        if verbose:
            console.print(f"[green]✓[/green] Authenticated successfully")
        
        # Upload file
        console.print(f"[blue]Uploading:[/blue] {file_path}")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Uploading and processing...", total=100)
                
                result = await api_client.upload_markdown(file_path)
                progress.update(task, completed=100)
            
            # Display results
            console.print(Panel(
                f"[green]✓[/green] Successfully uploaded [bold]{result['filename']}[/bold]\n\n"
                f"Game ID: [blue]{result['game_id']}[/blue]\n"
                f"Rules stored: [yellow]{result['rules_stored']}[/yellow]",
                title="Upload Complete"
            ))
            
        except FileNotFoundError:
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Upload failed:[/red] {str(e)}")
            raise typer.Exit(1)
        finally:
            await api_client.close()
    
    asyncio.run(_upload())

@app.command("list-games")
def list_games(
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show detailed information")
):
    """📋 List all registered games."""
    async def _list_games():
        # Authenticate
        with console.status("[bold blue]Authenticating...", spinner="dots"):
            if not await api_client.authenticate():
                raise typer.Exit(1)
        
        try:
            games = await api_client.list_games()
            
            if not games:
                console.print("[yellow]No games registered yet.[/yellow]")
                return
            
            # Create table
            table = Table(title="🎲 Registered Games")
            table.add_column("Game ID", style="blue")
            table.add_column("Name", style="bold")
            table.add_column("Rules", justify="center")
            table.add_column("Auto-Registered", justify="center")
            
            if verbose:
                table.add_column("Created", style="dim")
            
            for game in games:
                auto_reg = "✓" if game.get("auto_registered", False) else "✗"
                row = [
                    game["game_id"],
                    game["name"],
                    str(game.get("rule_count", 0)),
                    auto_reg
                ]
                
                if verbose and game.get("created_at"):
                    created_at = game["created_at"][:19] if isinstance(game["created_at"], str) else str(game["created_at"])
                    row.append(created_at)
                
                table.add_row(*row)
            
            console.print(table)
            console.print(f"\n[dim]Total games: {len(games)}[/dim]")
            
        except Exception as e:
            console.print(f"[red]Failed to list games:[/red] {str(e)}")
            raise typer.Exit(1)
        finally:
            await api_client.close()
    
    asyncio.run(_list_games())

@app.command("show-rules")
def show_rules(
    game_id: str = typer.Argument(..., help="Game ID to show rules for"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of rules shown")
):
    """📜 Show rules for a specific game."""
    async def _show_rules():
        # Authenticate
        with console.status("[bold blue]Authenticating...", spinner="dots"):
            if not await api_client.authenticate():
                raise typer.Exit(1)
        
        try:
            rules = await api_client.get_game_rules(game_id)
            
            if not rules:
                console.print(f"[yellow]No rules found for game: {game_id}[/yellow]")
                return
            
            console.print(f"\n[bold blue]Rules for {game_id}:[/bold blue]\n")
            
            for i, rule in enumerate(rules[:limit]):
                console.print(Panel(
                    f"[bold]{rule.get('title', 'Untitled')}[/bold]\n\n"
                    f"{rule.get('content', 'No content')[:200]}{'...' if len(rule.get('content', '')) > 200 else ''}",
                    title=f"Rule {i+1}",
                    border_style="blue"
                ))
            
            if len(rules) > limit:
                console.print(f"[dim]... and {len(rules) - limit} more rules[/dim]")
            
        except Exception as e:
            console.print(f"[red]Failed to show rules:[/red] {str(e)}")
            raise typer.Exit(1)
        finally:
            await api_client.close()
    
    asyncio.run(_show_rules())

@app.command("delete")
def delete_game(
    game_id: str = typer.Argument(..., help="Game ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """🗑️ Delete a game and all its rules."""
    async def _delete_game():
        if not force:
            if not Confirm.ask(f"[red]Are you sure you want to delete game '{game_id}' and all its rules?[/red]"):
                console.print("Cancelled.")
                return
        
        # Authenticate
        with console.status("[bold blue]Authenticating...", spinner="dots"):
            if not await api_client.authenticate():
                raise typer.Exit(1)
        
        try:
            with console.status(f"[red]Deleting game {game_id}...", spinner="dots"):
                result = await api_client.delete_game(game_id)
            
            console.print(Panel(
                f"[green]✓[/green] Successfully deleted game [bold]{game_id}[/bold]\n\n"
                f"Rules deleted: [yellow]{result['rules_deleted']}[/yellow]",
                title="Deletion Complete",
                border_style="red"
            ))
            
        except Exception as e:
            console.print(f"[red]Failed to delete game:[/red] {str(e)}")
            raise typer.Exit(1)
        finally:
            await api_client.close()
    
    asyncio.run(_delete_game())

@app.command("batch-upload")
def batch_upload(
    directory: Path = typer.Argument(..., help="Directory containing markdown files"),
    pattern: str = typer.Option("*.md", "--pattern", "-p", help="File pattern to match"),
    max_files: int = typer.Option(50, "--max", "-m", help="Maximum files to process")
):
    """📦 Upload multiple markdown files from a directory."""
    async def _batch_upload():
        if not directory.exists():
            console.print(f"[red]Directory not found:[/red] {directory}")
            raise typer.Exit(1)
        
        # Find markdown files
        files = list(directory.glob(pattern))[:max_files]
        
        if not files:
            console.print(f"[yellow]No files found matching pattern '{pattern}' in {directory}[/yellow]")
            return
        
        console.print(f"[blue]Found {len(files)} files to upload[/blue]")
        
        # Authenticate
        with console.status("[bold blue]Authenticating...", spinner="dots"):
            if not await api_client.authenticate():
                raise typer.Exit(1)
        
        # Batch upload with progress
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("Uploading files...", total=len(files))
                
                results = await api_client.batch_upload(files)
                
                progress.update(task, completed=len(files))
            
            # Display results summary
            successful = [r for r in results if r.get("success", False)]
            failed = [r for r in results if not r.get("success", False)]
            
            console.print(Panel(
                f"[green]✓[/green] Batch upload completed\n\n"
                f"Successful: [green]{len(successful)}[/green]\n"
                f"Failed: [red]{len(failed)}[/red]",
                title="Batch Upload Results"
            ))
            
            if failed:
                console.print("\n[red]Failed uploads:[/red]")
                for fail in failed:
                    console.print(f"  • {Path(fail['file_path']).name}: {fail.get('error', 'Unknown error')}")
            
        except Exception as e:
            console.print(f"[red]Batch upload failed:[/red] {str(e)}")
            raise typer.Exit(1)
        finally:
            await api_client.close()
    
    asyncio.run(_batch_upload())

@app.command("validate")
def validate_game(
    game_id: str = typer.Argument(..., help="Game ID to validate")
):
    """✅ Validate game rules integrity."""
    async def _validate():
        # Authenticate
        with console.status("[bold blue]Authenticating...", spinner="dots"):
            if not await api_client.authenticate():
                raise typer.Exit(1)
        
        try:
            with console.status(f"[blue]Validating game {game_id}...", spinner="dots"):
                result = await api_client.validate_game(game_id)
            
            is_valid = result.get("valid", False)
            issues = result.get("issues", [])
            
            if is_valid:
                console.print(f"[green]✓ Game '{game_id}' validation passed[/green]")
            else:
                console.print(f"[red]✗ Game '{game_id}' validation failed[/red]")
                if issues:
                    console.print("\n[red]Issues found:[/red]")
                    for issue in issues:
                        console.print(f"  • {issue}")
            
        except Exception as e:
            console.print(f"[red]Validation failed:[/red] {str(e)}")
            raise typer.Exit(1)
        finally:
            await api_client.close()
    
    asyncio.run(_validate())

@app.command("status")
def status():
    """📊 Show backend status and connection info."""
    async def _status():
        try:
            # Test connection
            response = await api_client.client.get(f"{api_client.base_url}/health")
            if response.status_code == 200:
                console.print(f"[green]✓[/green] Backend is running at [blue]{api_client.base_url}[/blue]")
                
                # Test authentication
                if await api_client.authenticate():
                    console.print("[green]✓[/green] Authentication successful")
                    
                    # Get basic stats
                    games = await api_client.list_games()
                    console.print(f"[blue]Games registered:[/blue] {len(games)}")
                else:
                    console.print("[red]✗[/red] Authentication failed")
            else:
                console.print(f"[red]✗[/red] Backend not responding: {response.status_code}")
                
        except Exception as e:
            console.print(f"[red]✗[/red] Connection failed: {str(e)}")
        finally:
            await api_client.close()
    
    asyncio.run(_status())

@app.command("config")
def config():
    """⚙️ Show current configuration."""
    console.print(Panel(
        f"[blue]API Base URL:[/blue] {api_client.base_url}\n"
        f"[blue]Environment:[/blue] {os.getenv('ENVIRONMENT', 'development')}\n"
        f"[blue]Config file:[/blue] {Path('.env').absolute() if Path('.env').exists() else 'Not found'}",
        title="Configuration"
    ))

if __name__ == "__main__":
    app()