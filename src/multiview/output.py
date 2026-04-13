"""Output formatters — terminal table, JSON, Markdown."""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .engine import Finding

SEVERITY_COLORS = {
    "CRITICAL": "bold red",
    "HIGH": "red",
    "MEDIUM": "yellow",
    "LOW": "cyan",
}

SEVERITY_EMOJI = {
    "CRITICAL": "[bold red]CRIT[/]",
    "HIGH": "[red]HIGH[/]",
    "MEDIUM": "[yellow]MED [/]",
    "LOW": "[cyan]LOW [/]",
}


def render_terminal(findings: list[Finding], timings: dict[str, float], file_path: str):
    console = Console()

    if not findings:
        console.print(Panel(
            "[bold green]No issues found.[/] All reviewers passed.",
            title=f"multiview: {file_path}",
            border_style="green",
        ))
        _print_timings(console, timings)
        return

    table = Table(
        title=f"multiview: {file_path}",
        show_lines=True,
        title_style="bold",
        border_style="dim",
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Sev", width=5, no_wrap=True)
    table.add_column("Location", style="cyan", width=20, no_wrap=True)
    table.add_column("Issue", min_width=40)
    table.add_column("Flagged by", style="dim", width=20)

    for i, f in enumerate(findings, 1):
        sev_text = SEVERITY_EMOJI.get(f.severity, f.severity)
        reviewers_str = ", ".join(f.reviewers)
        desc = f"[bold]{f.title}[/]\n{f.description}"
        if f.fix:
            desc += f"\n[dim]Fix: {f.fix}[/]"
        table.add_row(str(i), sev_text, f.location, desc, reviewers_str)

    console.print(table)

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    summary_parts = []
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if counts[sev]:
            color = SEVERITY_COLORS[sev]
            summary_parts.append(f"[{color}]{counts[sev]} {sev}[/]")
    console.print(f"\n  Total: {len(findings)} issues  ({', '.join(summary_parts)})")
    _print_timings(console, timings)


def _print_timings(console: Console, timings: dict[str, float]):
    parts = [f"[dim]{name}: {t:.1f}s[/]" for name, t in sorted(timings.items(), key=lambda x: x[1])]
    console.print(f"  Timings: {' | '.join(parts)}\n")


def render_json(findings: list[Finding], timings: dict[str, float], file_path: str) -> str:
    data = {
        "file": file_path,
        "total": len(findings),
        "findings": [
            {
                "severity": f.severity,
                "location": f.location,
                "title": f.title,
                "description": f.description,
                "fix": f.fix,
                "flagged_by": f.reviewers,
            }
            for f in findings
        ],
        "timings": timings,
    }
    return json.dumps(data, indent=2)


def render_markdown(findings: list[Finding], timings: dict[str, float], file_path: str) -> str:
    lines = [f"# Code Review: `{file_path}`\n"]

    if not findings:
        lines.append("**No issues found.** All reviewers passed.\n")
        return "\n".join(lines)

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    lines.append(f"**{len(findings)} issues found**\n")
    lines.append("| # | Severity | Location | Issue | Flagged by |")
    lines.append("|---|----------|----------|-------|------------|")

    for i, f in enumerate(findings, 1):
        reviewers = ", ".join(f.reviewers)
        desc = f"**{f.title}** {f.description}"
        if f.fix:
            desc += f" *Fix: {f.fix}*"
        lines.append(f"| {i} | {f.severity} | `{f.location}` | {desc} | {reviewers} |")

    lines.append("")
    lines.append("## Timings")
    for name, t in sorted(timings.items(), key=lambda x: x[1]):
        lines.append(f"- {name}: {t:.1f}s")

    return "\n".join(lines)
