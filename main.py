import sys
import asyncio
import typer
from loguru import logger
from rich.console import Console

# Mute verbose logs during CLI
logger.remove()
logger.add(sys.stderr, level="WARNING")

from langchain_core.messages import HumanMessage
from config import settings
from ui.terminal import print_banner, print_agent_status, render_response, print_system_table
from tools.rag_tools import ingest_document
from tools.system_tools import get_system_metrics
from tools.weather import get_live_weather
from tools.voice import speak_text, listen_to_speech
from memory import save_turn, store_semantic_memory

app = typer.Typer(help="Captain: Desktop Multi-Agent AI Ecosystem")
console = Console()


@app.command()
def chat():
    """Unified Interactive Multi-Agent Terminal Chat (V2 Engine)."""
    asyncio.run(_chat_async())


async def _chat_async():
    """Async chat loop — all V2 asyncio primitives live in one event loop."""
    from src.agents.agent_registry import AgentRegistry
    from src.agents.agent_lifecycle_manager import AgentLifecycleManager
    from src.agents.conversation_agent import ConversationAgent
    from src.agents.coding_agent import CodingAgent
    from src.agents.system_agent import SystemAgent
    from src.agents.rag_agent import RagAgent
    from src.agents.search_agent import SearchAgent
    from src.agents.comms_agent import CommsAgent
    from src.graph.state_graph import create_captain_graph
    from src.backend.core.event_bus import event_bus

    print_banner()

    # --- V2 Setup: Register & Initialize All 6 Agents ---
    registry = AgentRegistry()
    for agent in [ConversationAgent(), CodingAgent(), SystemAgent(),
                  RagAgent(), SearchAgent(), CommsAgent()]:
        await registry.register_agent(agent)

    manager = AgentLifecycleManager(registry, event_bus)
    graph = create_captain_graph(registry, manager)
    thread_config = {"configurable": {"thread_id": "captain_session_1"}}
    tts_enabled = True

    console.print("\n[bold green]Captain V2 is ready! (5 agents: Chat | Coder | System | RAG | Search)[/bold green]")
    console.print("[bold yellow]🔊 Voice Output is ACTIVE! Captain will speak all answers aloud.[/bold yellow]")
    console.print("[dim]Type your message, or type [bold cyan]v[/bold cyan] (or [bold cyan]voice[/bold cyan]) to speak into mic. Type [bold cyan]/tts[/bold cyan] to mute audio.[/dim]")
    console.print("[dim]Type [bold cyan]/clear[/bold cyan] to clear session memory. Type [bold cyan]/history[/bold cyan] to view memory.[/dim]\n")

    # Stable session ID for this run
    session_id = f"captain_session_{id(graph)}"

    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, lambda: console.input("[bold cyan]You > [/bold cyan]").strip()
            )
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Exiting Captain Assistant. Have a great day![/yellow]")
                break

            # Toggle TTS
            if user_input.lower() in ["/tts", "tts"]:
                tts_enabled = not tts_enabled
                status_str = "ENABLED 🔊" if tts_enabled else "MUTED 🔇"
                console.print(f"[bold yellow]Spoken Voice Output is now {status_str}[/bold yellow]")
                continue

            # Clear session memory
            if user_input.lower() in ["/clear", "clear memory"]:
                from memory.session_memory import clear_session
                deleted = clear_session(session_id)
                console.print(f"[bold yellow]Session memory cleared ({deleted} turns removed).[/bold yellow]")
                continue

            # Show session memory
            if user_input.lower() in ["/history", "show history"]:
                from memory.session_memory import get_history
                history = get_history(session_id)
                if history:
                    console.print(f"[dim]--- Last {len(history)} turns ---[/dim]")
                    for t in history:
                        color = "cyan" if t["role"] == "user" else "green"
                        console.print(f"[{color}]{t['role'].upper()}:[/{color}] {t['content'][:120]}")
                else:
                    console.print("[dim]No history in this session.[/dim]")
                continue

            # Voice Input
            voice_triggers = {"v", "/v", "voice", "/voice", "speak", "/speak", "mic", "/mic"}
            if user_input.lower() in voice_triggers:
                console.print("\n[bold yellow]🎙️ Microphone Active! Recording audio for 5 seconds...[/bold yellow]")
                spoken = await asyncio.get_event_loop().run_in_executor(None, lambda: listen_to_speech(duration=5))
                if spoken:
                    console.print(f"[bold green]Heard Speech:[/bold green] {spoken}\n")
                    user_input = spoken
                else:
                    console.print("[bold red]No speech detected.[/bold red]\n")
                    continue

            # Add current user turn to messages so LangGraph accumulates full history
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_query": user_input,
                "current_agent": "",
                "next_agent": "",
                "task_plan": [],
                "scratchpad": {},
                "error": None,
            }

            with console.status("[bold green]Captain is processing...[/bold green]", spinner="dots"):
                final_state = await graph.ainvoke(initial_state, config=thread_config)

            messages = final_state.get("messages", [])
            current_agent = final_state.get("current_agent", "Captain")

            if messages:
                last_msg = messages[-1].content
                render_response(current_agent, last_msg)
                # Persist turn to Supabase PostgreSQL & index into ChromaDB
                import time
                turn_id = f"turn_{int(time.time() * 1000)}"
                save_turn("captain_session_1", "user", user_input)
                save_turn("captain_session_1", "assistant", last_msg)
                store_semantic_memory(turn_id, f"User asked: {user_input} | Captain responded: {last_msg}", {"session_id": "captain_session_1"})
                if tts_enabled:
                    speak_text(last_msg)
            else:
                fallback_text = "I am here! How can I assist you today?"
                render_response("Captain", fallback_text)
                if tts_enabled:
                    speak_text(fallback_text)

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Exiting.[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def desktop():
    """Launch Voice-Reactive Animated Avatar Desktop Window."""
    console.print("[bold green]Launching Captain Animated Voice Desktop App...[/bold green]")
    from ui.desktop_gui import launch_desktop_gui
    launch_desktop_gui()


@app.command()
def ingest(file_path: str):
    """Ingest a PDF or document into the RAG vectorstore."""
    console.print(f"[cyan]Ingesting document:[/cyan] {file_path}")
    res = ingest_document(file_path)
    if res.get("status") == "success":
        console.print(f"[bold green]Success![/bold green] Indexed {res.get('chunks_indexed')} chunks from {res.get('file')}.")
    else:
        console.print(f"[bold red]Failed:[/bold red] {res.get('error')}")


@app.command()
def metrics():
    """View hardware performance stats (CPU, RAM, Disk)."""
    m = get_system_metrics()
    if m.get("status") == "success":
        print_system_table(m)
    else:
        console.print(f"[red]Error:[/red] {m.get('error')}")


@app.command()
def weather(city: str = "New York"):
    """Get live weather for any city."""
    w = get_live_weather(city)
    if w.get("status") == "success":
        console.print(f"[bold green]Weather for {w['city']}, {w['country']}:[/bold green] {w['temperature_celsius']}°C | Wind: {w['windspeed_kmh']} km/h")
    else:
        console.print(f"[red]Error:[/red] {w.get('error')}")


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
):
    """Start the Captain FastAPI server (REST + WebSocket + Web UI)."""
    console.print(f"[bold green]Starting Captain API Server at http://{host}:{port}[/bold green]")
    console.print(f"[dim]  • REST API:  http://{host}:{port}/api/v1/chat[/dim]")
    console.print(f"[dim]  • Web UI:    http://{host}:{port}/ui[/dim]")
    console.print(f"[dim]  • API Docs:  http://{host}:{port}/docs[/dim]")
    from src.backend.main import start_server
    start_server(host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
