#!/usr/bin/env python3
"""
CLI tool to review and manage LLM conversation insights

Usage:
    python tools/insights_cli.py list
    python tools/insights_cli.py list --priority high
    python tools/insights_cli.py list --type action_item --days 7
    python tools/insights_cli.py stats
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import click
except ImportError:
    print("Error: 'click' package not installed")
    print("Install with: pip install click")
    sys.exit(1)

INSIGHTS_DIR = Path("llm_insights")


@click.group()
def cli():
    """LLM Insights Manager - Review conversation insights from LLMs"""
    pass


@cli.command()
@click.option('--type', '-t', help='Filter by type (action_item, idea, decision, question, note, risk)')
@click.option('--priority', '-p', help='Filter by priority (high, medium, low)')
@click.option('--days', '-d', type=int, help='Only show insights from last N days')
@click.option('--limit', '-l', type=int, default=20, help='Limit number of results')
@click.option('--conversation', '-c', help='Filter by conversation ID')
def list(type, priority, days, limit, conversation):
    """List all insights"""
    if not INSIGHTS_DIR.exists():
        click.echo(f"❌ Insights directory not found: {INSIGHTS_DIR.absolute()}")
        click.echo("No insights have been collected yet.")
        return

    insights = _load_insights(
        type_filter=type,
        priority_filter=priority,
        days_filter=days,
        conversation_filter=conversation
    )

    if not insights:
        click.echo("No insights found matching your criteria.")
        return

    click.echo(f"\n📊 Found {len(insights)} insight(s)\n")
    click.echo("=" * 80)

    for i, insight in enumerate(insights[:limit], 1):
        _display_insight(insight, number=i)
        if i < min(len(insights), limit):
            click.echo("-" * 80)

    if len(insights) > limit:
        click.echo(f"\n... and {len(insights) - limit} more. Use --limit to see more.")


@cli.command()
@click.option('--type', '-t', help='Filter by type')
@click.option('--days', '-d', type=int, help='Stats for last N days')
def stats(type, days):
    """Show statistics about collected insights"""
    if not INSIGHTS_DIR.exists():
        click.echo(f"❌ Insights directory not found: {INSIGHTS_DIR.absolute()}")
        return

    insights = _load_insights(type_filter=type, days_filter=days)

    if not insights:
        click.echo("No insights found.")
        return

    # Count by type
    by_type = {}
    by_priority = {}
    by_conversation = {}
    tags_count = {}

    for insight_data in insights:
        insight = insight_data.get("insight", {})
        conv = insight_data.get("conversation", {})

        # Type count
        itype = insight.get("type", "unknown")
        by_type[itype] = by_type.get(itype, 0) + 1

        # Priority count
        priority = insight.get("priority", "unknown")
        by_priority[priority] = by_priority.get(priority, 0) + 1

        # Conversation count
        conv_id = conv.get("id", "unknown")
        by_conversation[conv_id] = by_conversation.get(conv_id, 0) + 1

        # Tags count
        for tag in insight.get("tags", []):
            tags_count[tag] = tags_count.get(tag, 0) + 1

    click.echo("\n📊 Insight Statistics\n")
    click.echo(f"Total Insights: {len(insights)}")

    if days:
        click.echo(f"Time Period: Last {days} days")

    click.echo("\n" + "=" * 60)

    click.echo("\n📋 By Type:")
    for t, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count, 40)
        click.echo(f"  {t:20} {count:3}  {bar}")

    click.echo("\n🎯 By Priority:")
    priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
    for p in ["high", "medium", "low"]:
        if p in by_priority:
            count = by_priority[p]
            bar = "█" * min(count, 40)
            click.secho(f"  {p:20} {count:3}  {bar}", fg=priority_colors.get(p))

    click.echo("\n💬 By Conversation:")
    top_conversations = sorted(by_conversation.items(), key=lambda x: x[1], reverse=True)[:10]
    for conv_id, count in top_conversations:
        bar = "█" * min(count, 40)
        conv_short = conv_id[:30] + "..." if len(conv_id) > 30 else conv_id
        click.echo(f"  {conv_short:33} {count:3}  {bar}")

    if tags_count:
        click.echo("\n🏷️  Top Tags:")
        top_tags = sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in top_tags:
            bar = "█" * min(count, 40)
            click.echo(f"  {tag:20} {count:3}  {bar}")


@cli.command()
@click.option('--type', '-t', help='Export specific type')
@click.option('--priority', '-p', help='Export specific priority')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'markdown']), default='json', help='Export format')
@click.option('--output', '-o', help='Output file path')
def export(type, priority, format, output):
    """Export insights to file"""
    insights = _load_insights(type_filter=type, priority_filter=priority)

    if not insights:
        click.echo("No insights to export.")
        return

    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"insights_export_{timestamp}.{format}"

    output_path = Path(output)

    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2)

    elif format == 'csv':
        import csv
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(['Timestamp', 'Type', 'Priority', 'Title', 'Content', 'Conversation ID', 'Tags'])

            # Data
            for insight_data in insights:
                insight = insight_data.get("insight", {})
                conv = insight_data.get("conversation", {})
                writer.writerow([
                    insight_data.get("timestamp", ""),
                    insight.get("type", ""),
                    insight.get("priority", ""),
                    insight.get("title", ""),
                    insight.get("content", ""),
                    conv.get("id", ""),
                    ", ".join(insight.get("tags", []))
                ])

    elif format == 'markdown':
        with open(output_path, 'w') as f:
            f.write("# LLM Insights Export\n\n")
            f.write(f"Exported: {datetime.now().isoformat()}\n")
            f.write(f"Total Insights: {len(insights)}\n\n")
            f.write("---\n\n")

            for insight_data in insights:
                insight = insight_data.get("insight", {})
                conv = insight_data.get("conversation", {})

                f.write(f"## {insight.get('title', 'Untitled')}\n\n")
                f.write(f"- **Type**: {insight.get('type', 'N/A')}\n")
                f.write(f"- **Priority**: {insight.get('priority', 'N/A')}\n")
                f.write(f"- **Timestamp**: {insight_data.get('timestamp', 'N/A')}\n")
                f.write(f"- **Conversation**: {conv.get('id', 'N/A')}\n")

                if insight.get('tags'):
                    f.write(f"- **Tags**: {', '.join(insight['tags'])}\n")

                f.write(f"\n{insight.get('content', '')}\n\n")

                if insight.get('suggested_followup'):
                    f.write(f"**Suggested Followup**: {insight['suggested_followup']}\n\n")

                f.write("---\n\n")

    click.echo(f"✅ Exported {len(insights)} insights to {output_path.absolute()}")


@cli.command()
def clean():
    """Clean up old insights (interactive)"""
    if not INSIGHTS_DIR.exists():
        click.echo("No insights directory found.")
        return

    insights = _load_all_files()

    if not insights:
        click.echo("No insights to clean.")
        return

    click.echo(f"Found {len(insights)} total insights")

    days = click.prompt("Delete insights older than how many days?", type=int, default=90)

    cutoff = datetime.now() - timedelta(days=days)
    to_delete = []

    for filepath, data in insights:
        file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        if file_time < cutoff:
            to_delete.append((filepath, data))

    if not to_delete:
        click.echo(f"No insights older than {days} days.")
        return

    click.echo(f"\nFound {len(to_delete)} insights older than {days} days:")
    for filepath, _ in to_delete[:5]:
        click.echo(f"  - {filepath.name}")

    if len(to_delete) > 5:
        click.echo(f"  ... and {len(to_delete) - 5} more")

    if click.confirm(f"\nDelete {len(to_delete)} insights?"):
        for filepath, _ in to_delete:
            filepath.unlink()
        click.echo(f"✅ Deleted {len(to_delete)} insights")
    else:
        click.echo("Cancelled.")


def _load_insights(type_filter=None, priority_filter=None, days_filter=None, conversation_filter=None):
    """Load insights from disk with filters"""
    insights = []

    if type_filter:
        # Convert type to plural directory name
        type_dir = type_filter + "s" if not type_filter.endswith("s") else type_filter
        dirs = [INSIGHTS_DIR / type_dir]
    else:
        dirs = [d for d in INSIGHTS_DIR.iterdir() if d.is_dir()]

    cutoff_date = datetime.now() - timedelta(days=days_filter) if days_filter else None

    for dir_path in dirs:
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("*.json"):
            # Check date if filter specified
            if cutoff_date:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    continue

            try:
                with open(file_path) as f:
                    insight_data = json.load(f)

                    # Filter by priority
                    if priority_filter:
                        if insight_data.get("insight", {}).get("priority") != priority_filter:
                            continue

                    # Filter by conversation
                    if conversation_filter:
                        if insight_data.get("conversation", {}).get("id") != conversation_filter:
                            continue

                    insights.append(insight_data)
            except (json.JSONDecodeError, IOError) as e:
                click.echo(f"⚠️  Error reading {file_path}: {e}", err=True)

    # Sort by timestamp, newest first
    insights.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return insights


def _load_all_files():
    """Load all insight files with their paths"""
    results = []
    dirs = [d for d in INSIGHTS_DIR.iterdir() if d.is_dir()]

    for dir_path in dirs:
        for file_path in dir_path.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    results.append((file_path, data))
            except (json.JSONDecodeError, IOError):
                pass

    return results


def _display_insight(insight_data, number=None):
    """Display insight in terminal"""
    insight = insight_data.get("insight", {})
    conv = insight_data.get("conversation", {})
    metadata = insight_data.get("metadata", {})

    type_emoji = {
        "action_item": "✅",
        "idea": "💡",
        "decision": "🎯",
        "question": "❓",
        "note": "📝",
        "risk": "⚠️"
    }

    emoji = type_emoji.get(insight.get("type"), "📌")
    priority = insight.get("priority", "medium")
    priority_color = "red" if priority == "high" else "yellow" if priority == "medium" else "green"

    timestamp = insight_data.get("timestamp", "")[:19].replace("T", " ")

    # Header line
    if number:
        click.echo(f"\n{number}. ", nl=False)

    click.echo(f"{emoji} [{timestamp}] ", nl=False)
    click.secho(f"{priority.upper():6}", fg=priority_color, bold=True, nl=False)
    click.echo(f" - {insight.get('title', 'Untitled')}")

    # Context and content
    context = conv.get("context", "")
    if context:
        click.echo(f"   📍 Context: {context}")

    content = insight.get("content", "")
    if content:
        # Wrap content if too long
        if len(content) > 200:
            content_preview = content[:197] + "..."
        else:
            content_preview = content
        click.echo(f"   💬 {content_preview}")

    # Tags
    if insight.get("tags"):
        tags_str = ", ".join(insight["tags"])
        click.echo(f"   🏷️  {tags_str}")

    # Suggested followup
    if insight.get("suggested_followup"):
        click.echo(f"   💭 Suggested: {insight['suggested_followup']}")

    # Metadata
    if metadata.get("llm_model"):
        click.echo(f"   🤖 Model: {metadata['llm_model']}", nl=False)
        if metadata.get("confidence"):
            click.echo(f" (confidence: {metadata['confidence']:.0%})")
        else:
            click.echo()


if __name__ == "__main__":
    cli()
