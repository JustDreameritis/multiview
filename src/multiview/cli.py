"""CLI entry point — setup, review, version."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from . import __version__
from .config import (
    CONFIG_FILE,
    DEFAULT_REVIEWERS,
    PROVIDERS,
    get_configured_providers,
    load_config,
    save_config,
)
from .engine import run_review
from .output import render_json, render_markdown, render_terminal
from .ask_engine import ask, get_configured_perspectives, ASK_PERSPECTIVES

console = Console()

MAX_FILE_SIZE = 100_000  # 100KB
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".rb", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".swift", ".kt", ".scala",
    ".sh", ".bash", ".yaml", ".yml", ".toml", ".json", ".sql",
}


@click.group()
@click.version_option(__version__, prog_name="multiview")
def main():
    """Multi-model AI code review from your terminal."""


@main.command()
def setup():
    """Configure API keys for each provider (all free tier)."""
    console.print("\n[bold]multiview setup[/]\n")
    console.print("Each provider offers a free API tier. No credit card required.\n")

    config = load_config()
    keys = config.get("api_keys", {})

    for provider_id, info in PROVIDERS.items():
        current = keys.get(provider_id, "")
        status = "[green]configured[/]" if current else "[dim]not set[/]"
        console.print(f"  [bold]{info['name']}[/] ({status})")
        console.print(f"  Sign up: [link={info['signup_url']}]{info['signup_url']}[/link]")

        key = click.prompt(
            f"  {info['env_var']}",
            default=current or "",
            show_default=False,
        )
        if key:
            keys[provider_id] = key.strip()
        console.print()

    config["api_keys"] = keys
    save_config(config)

    configured = sum(1 for v in keys.values() if v)
    console.print(f"[green]Saved to {CONFIG_FILE}[/]")
    console.print(f"[bold]{configured}/{len(PROVIDERS)} providers configured.[/]\n")


@main.command()
def status():
    """Show which providers are configured and which reviewers are active."""
    configured = get_configured_providers()

    console.print(f"\n[bold]multiview status[/]  (config: {CONFIG_FILE})\n")

    for r in DEFAULT_REVIEWERS:
        active = r.provider in configured
        icon = "[green]ON [/]" if active else "[red]OFF[/]"
        console.print(f"  {icon}  {r.name:15s}  {r.model}")

    active_count = sum(1 for r in DEFAULT_REVIEWERS if r.provider in configured)
    console.print(f"\n  {active_count}/{len(DEFAULT_REVIEWERS)} reviewers active.")
    if active_count < len(DEFAULT_REVIEWERS):
        console.print("  Run [bold]multiview setup[/] to configure missing providers.\n")
    else:
        console.print()


@main.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--markdown", "output_md", is_flag=True, help="Output as Markdown")
@click.option("--model", "filter_model", multiple=True, help="Only use these reviewers (by name)")
def review(target: str, output_json: bool, output_md: bool, filter_model: tuple[str]):
    """Review a file or directory with all configured models."""
    target_path = Path(target)

    # Collect files
    if target_path.is_file():
        files = [target_path]
    elif target_path.is_dir():
        files = sorted(
            f for f in target_path.rglob("*")
            if f.is_file()
            and f.suffix in SUPPORTED_EXTENSIONS
            and f.stat().st_size <= MAX_FILE_SIZE
            and ".git" not in f.parts
            and "node_modules" not in f.parts
            and "__pycache__" not in f.parts
            and ".venv" not in f.parts
        )
    else:
        console.print("[red]Target must be a file or directory.[/]")
        sys.exit(1)

    if not files:
        console.print("[yellow]No supported files found.[/]")
        sys.exit(1)

    # Filter reviewers
    configured = get_configured_providers()
    reviewers = [r for r in DEFAULT_REVIEWERS if r.provider in configured]

    if filter_model:
        names_lower = {n.lower() for n in filter_model}
        reviewers = [r for r in reviewers if r.name.lower() in names_lower]

    if not reviewers:
        console.print("[red]No reviewers available. Run 'multiview setup' first.[/]")
        sys.exit(1)

    for file_path in files:
        code = file_path.read_text(errors="replace")
        if not code.strip():
            continue

        # Truncate large files to avoid token limits
        if len(code) > 15_000:
            code = code[:15_000] + "\n\n# ... truncated (file too large for review) ..."

        rel_path = str(file_path)

        if not output_json and not output_md:
            console.print(f"\n[bold]Reviewing {rel_path}[/] with {len(reviewers)} models...\n")

            def on_done(name, success, elapsed, count=0):
                if success:
                    console.print(f"  [green]OK[/]  {name:15s}  {elapsed:.1f}s  ({count} findings)")
                else:
                    console.print(f"  [red]ERR[/] {name:15s}  {elapsed:.1f}s  (failed)")

            findings, timings = run_review(code, rel_path, reviewers, on_reviewer_done=on_done)
            console.print()
            render_terminal(findings, timings, rel_path)

        elif output_json:
            findings, timings = run_review(code, rel_path, reviewers)
            click.echo(render_json(findings, timings, rel_path))

        elif output_md:
            findings, timings = run_review(code, rel_path, reviewers)
            click.echo(render_markdown(findings, timings, rel_path))


@main.command("ask")
@click.argument("question")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def ask_command(question: str, output_json: bool):
    """Ask a question to multiple AI perspectives in parallel.

    QUESTION: The question to analyze from multiple angles.

    Example: multiview ask "What causes inflation?"
    """
    from rich.panel import Panel
    from rich.markdown import Markdown
    import json

    perspectives = get_configured_perspectives()
    if not perspectives:
        console.print("[red]No perspectives available. Run 'multiview setup' first.[/]")
        sys.exit(1)

    console.print(f"\n[bold]multiview ask[/] — {len(perspectives)} perspectives\n")
    console.print(f"[dim]Question:[/] {question}\n")

    def on_done(name, success, elapsed):
        if success:
            console.print(f"  [green]OK[/]  {name:18s}  {elapsed:.1f}s")
        else:
            console.print(f"  [red]ERR[/] {name:18s}  {elapsed:.1f}s")

    responses, consensus = ask(question, on_perspective_done=on_done)

    if output_json:
        data = {
            "question": question,
            "perspectives": [
                {
                    "name": r.name,
                    "response": r.response,
                    "elapsed": r.elapsed,
                    "success": r.success,
                }
                for r in responses
            ],
            "consensus": consensus,
        }
        click.echo(json.dumps(data, indent=2))
        return

    # Terminal output
    console.print("\n" + "=" * 70 + "\n")

    for r in responses:
        if r.success:
            console.print(Panel(
                r.response,
                title=f"[bold]{r.name}[/] ({r.elapsed:.1f}s)",
                border_style="blue",
            ))
        else:
            console.print(Panel(
                f"[red]{r.response}[/]",
                title=f"[bold]{r.name}[/] (failed)",
                border_style="red",
            ))

    # Consensus section
    console.print("\n" + "=" * 70)
    console.print(Panel(
        Markdown(consensus),
        title="[bold yellow]CONSENSUS[/]",
        border_style="yellow",
    ))

    # Summary
    successful = sum(1 for r in responses if r.success)
    total_time = sum(r.elapsed for r in responses)
    console.print(f"\n  [dim]{successful}/{len(responses)} perspectives responded | Total time: {total_time:.1f}s[/]\n")


if __name__ == "__main__":
    main()
