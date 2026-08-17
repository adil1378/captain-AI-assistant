import asyncio
import math
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
from langchain_core.messages import HumanMessage
from tools.voice import listen_to_speech, speak_text
from utils.text_utils import clean_think_tags
from memory import save_turn, store_semantic_memory
from loguru import logger


def _build_v2_graph_sync():
    """
    Build the full 6-agent V2 LangGraph engine synchronously for Tkinter.
    Returns the compiled graph.
    """
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

    loop = asyncio.new_event_loop()

    async def _setup():
        registry = AgentRegistry()
        for agent in [ConversationAgent(), CodingAgent(), SystemAgent(),
                      RagAgent(), SearchAgent(), CommsAgent()]:
            await registry.register_agent(agent)

        manager = AgentLifecycleManager(registry, event_bus)
        return create_captain_graph(registry, manager)

    graph = loop.run_until_complete(_setup())
    loop.close()
    return graph


class CaptainDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Captain AI OS — Desktop Avatar")
        self.root.geometry("450x650")
        self.root.configure(bg="#0d1117")

        # V2 graph (compiled once)
        self.graph = _build_v2_graph_sync()

        # State Variables
        self.is_listening = False
        self.is_speaking = False
        self.phase = 0.0

        self._build_ui()
        self.animate_avatar()

    def _build_ui(self):
        # Header / Status
        header_frame = tk.Frame(self.root, bg="#0d1117")
        header_frame.pack(fill=tk.X, pady=10)

        title_label = tk.Label(
            header_frame,
            text="CAPTAIN AI OS",
            font=("Segoe UI", 16, "bold"),
            fg="#58a6ff",
            bg="#0d1117"
        )
        title_label.pack()

        self.status_label = tk.Label(
            header_frame,
            text="● STANDBY",
            font=("Segoe UI", 10, "bold"),
            fg="#8b949e",
            bg="#0d1117"
        )
        self.status_label.pack()

        # Canvas Avatar
        self.canvas = tk.Canvas(self.root, width=220, height=220, bg="#0d1117", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Chat ScrolledText Display
        self.chat_box = scrolledtext.ScrolledText(
            self.root,
            width=48,
            height=12,
            font=("Consolas", 9),
            bg="#161b22",
            fg="#c9d1d9",
            insertbackground="white",
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_box.pack(pady=5, px=10)

        # Controls & Input
        btn_frame = tk.Frame(self.root, bg="#0d1117")
        btn_frame.pack(pady=5)

        self.voice_btn = tk.Button(
            btn_frame,
            text="🎤 Speak to Captain",
            font=("Segoe UI", 10, "bold"),
            bg="#238636",
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            relief="flat",
            command=self.toggle_voice
        )
        self.voice_btn.pack(side=tk.LEFT, padx=5)

        # Text input
        self.text_entry = tk.Entry(
            self.root,
            font=("Segoe UI", 10),
            bg="#21262d",
            fg="#c9d1d9",
            insertbackground="white",
            relief="flat",
            width=38
        )
        self.text_entry.pack(pady=5)
        self.text_entry.bind("<Return>", self._on_text_submit)

        send_btn = tk.Button(
            self.root,
            text="Send ➤",
            font=("Segoe UI", 9, "bold"),
            bg="#1f6beb",
            fg="white",
            activebackground="#388bfd",
            activeforeground="white",
            relief="flat",
            command=self._on_text_submit
        )
        send_btn.pack(pady=3)

    def _on_text_submit(self, event=None):
        query = self.text_entry.get().strip()
        if not query:
            return
        self.text_entry.delete(0, tk.END)
        self.append_chat("YOU", query)
        threading.Thread(target=self.process_query, args=(query,), daemon=True).start()

    def append_chat(self, sender: str, text: str):
        """Append text to ScrolledText box thread-safely."""
        def _update():
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, f"{sender}: ", "bold")
            self.chat_box.insert(tk.END, f"{text}\n\n")
            self.chat_box.tag_config("bold", font=("Segoe UI", 9, "bold"), foreground="#58a6ff" if sender == "CAPTAIN" else "#79c0ff")
            self.chat_box.see(tk.END)
            self.chat_box.config(state=tk.DISABLED)
        self.root.after(0, _update)

    def set_status(self, status: str, color: str):
        """Thread-safe status label update."""
        self.root.after(0, lambda: self.status_label.config(text=f"● {status}", fg=color))

    def toggle_voice(self):
        if not self.is_listening:
            self.is_listening = True
            self.voice_btn.config(text="🎙 Listening...", bg="#da3633")
            self.set_status("LISTENING...", "#f85149")
            threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        spoken = listen_to_speech(duration=5)
        self.root.after(0, lambda: setattr(self, 'is_listening', False))
        self.root.after(0, lambda: self.voice_btn.config(text="🎤 Speak to Captain", bg="#238636"))

        if spoken:
            self.append_chat("YOU (Voice)", spoken)
            self.process_query(spoken)
        else:
            self.set_status("STANDBY", "#8b949e")

    def process_query(self, query: str):
        """Execute query via V2 graph in a bg thread."""
        self.set_status("THINKING...", "#d29922")
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "current_agent": "",
            "next_agent": "",
            "task_plan": [],
            "scratchpad": {},
            "error": None
        }

        try:
            loop = asyncio.new_event_loop()
            final_state = loop.run_until_complete(
                self.graph.ainvoke(
                    initial_state,
                    config={"configurable": {"thread_id": "desktop_session"}}
                )
            )
            loop.close()

            messages = final_state.get("messages", [])
            last_msg = messages[-1].content if messages else "Done."
            clean_msg = clean_think_tags(last_msg)

            # Persist to Supabase & ChromaDB
            turn_id = f"desktop_turn_{int(time.time() * 1000)}"
            save_turn("desktop_session", "user", query)
            save_turn("desktop_session", "assistant", clean_msg)
            store_semantic_memory(turn_id, f"User asked: {query} | Captain responded: {clean_msg}", {"session_id": "desktop_session"})

            self.append_chat("CAPTAIN", clean_msg)
            self.set_status("SPEAKING...", "#238636")
            self.root.after(0, lambda: setattr(self, 'is_speaking', True))

            speak_text(clean_msg)

            self.root.after(0, lambda: setattr(self, 'is_speaking', False))
            self.set_status("STANDBY", "#8b949e")
        except Exception as e:
            logger.error(f"DesktopGUI process_query error: {e}")
            self.append_chat("SYSTEM ERROR", str(e))
            self.set_status("ERROR", "#f85149")

    def animate_avatar(self):
        self.canvas.delete("all")
        cx, cy = 110, 110
        self.phase += 0.08

        if self.is_listening:
            base_r = 55 + math.sin(self.phase * 2) * 12
            color = "#f85149"
        elif self.is_speaking:
            base_r = 50 + math.cos(self.phase * 3) * 10
            color = "#3fb950"
        else:
            base_r = 45 + math.sin(self.phase) * 4
            color = "#58a6ff"

        # Inner Glow Circle
        self.canvas.create_oval(
            cx - base_r, cy - base_r,
            cx + base_r, cy + base_r,
            fill=color, outline="#1f6beb", width=2
        )

        # Outer Pulsing Rings
        for i in range(1, 4):
            ring_r = base_r + (i * 12) + (math.sin(self.phase + i) * 5)
            self.canvas.create_oval(
                cx - ring_r, cy - ring_r,
                cx + ring_r, cy + ring_r,
                outline=color, width=1
            )

        self.root.after(30, self.animate_avatar)


def launch_desktop_gui():
    root = tk.Tk()
    app = CaptainDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_desktop_gui()
