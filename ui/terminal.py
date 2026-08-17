from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from config import settings

console = Console()


def print_banner():
    """Print clean, beautiful title banner for Captain Assistant in terminal."""
    banner_text = Text()
    banner_text.append("   _____          _____ _______  ░░░\n", style="bold cyan")
    banner_text.append("  / ____|   /\\   |  __ \\__   __| ░░░\n", style="bold cyan")
    banner_text.append(" | |       /  \\  | |__) | | |    ░░░\n", style="bold blue")
    banner_text.append(" | |      / /\\ \\ |  ___/  | |    \n", style="bold blue")
    banner_text.append(" | |____ / ____ \\| |      | |    \n", style="bold magenta")
    banner_text.append("  \\_____/_/    \\_\\_|      |_|    \n", style="bold magenta")

    subtitle = f"[bold white]Multi-Agent Ecosystem[/bold white] | Chat: [bold green]{settings.chat_model}[/bold green] | Coder: [bold yellow]{settings.coder_model}[/bold yellow] | RAG: [bold cyan]{settings.rag_model}[/bold cyan]"
    panel = Panel(
        Text.from_markup(f"{banner_text}\n{subtitle}"),
        border_style="bold cyan",
        title="[bold green]⚡ CAPTAIN AI ECOSYSTEM[/bold green]",
        subtitle="[dim]Type 'exit' or 'quit' to close[/dim]"
    )
    console.print(panel)


def print_agent_status(agent_name: str, status: str = "Active"):
    """Display colored status badge for executing sub-agent."""
    color_map = {
        "master_supervisor": "magenta",
        "chat_agent": "bold white",
        "coder_agent": "green",
        "rag_agent": "yellow",
        "search_agent": "blue",
        "comms_agent": "red",
        "system_agent": "cyan"
    }
    color = color_map.get(agent_name, "white")
    console.print(f"[{color}]⚡ Agent [{agent_name.upper()}]: {status}...[/{color}]")


def render_response(agent_name: str, text: str):
    """Render agent response cleanly in a styled Rich Panel."""
    md = Markdown(text)
    
    agent_titles = {
        "chat_agent": "💬 Captain Chat",
        "coder_agent": "💻 CoderAgent",
        "rag_agent": "📚 RAGAgent",
        "search_agent": "🌐 SearchAgent",
        "comms_agent": "📬 CommsAgent",
        "system_agent": "⚙️ SystemAgent",
    }
    title_str = agent_titles.get(agent_name, f"⚡ {agent_name}")

    panel = Panel(
        md,
        title=f"[bold green]{title_str}[/bold green]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def print_system_table(metrics: dict):
    """Render hardware metrics in a structured Rich Table."""
    table = Table(title="🖥️ System Hardware Metrics", border_style="cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bold green")

    cpu_pct = metrics.get('cpu_usage_percent', metrics.get('cpu_percent', 0))
    ram = metrics.get('ram', {})
    ram_used = metrics.get('memory_used_gb', ram.get('used_gb', 0))
    ram_total = metrics.get('memory_total_gb', ram.get('total_gb', 0))
    ram_pct = metrics.get('memory_percent', ram.get('percent', 0))

    disk = metrics.get('disk', {})
    disk_used = metrics.get('disk_used_gb', disk.get('used_gb', 0))
    disk_total = metrics.get('disk_total_gb', disk.get('total_gb', 0))
    disk_pct = metrics.get('disk_percent', disk.get('percent', 0))

    battery = metrics.get('battery', {})
    batt_pct = metrics.get('battery_percent', battery.get('percent', 100))

    table.add_row("CPU Load", f"{cpu_pct}%")
    table.add_row("RAM Usage", f"{ram_used} GB / {ram_total} GB ({ram_pct}%)")
    table.add_row("Disk Usage", f"{disk_used} GB / {disk_total} GB ({disk_pct}%)")
    table.add_row("Battery", f"{batt_pct}%")

    console.print(table)
