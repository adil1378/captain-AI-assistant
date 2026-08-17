# captain







I create a ai agent its handle all things like chatting its also speak and able to listening and its also have features like its give weather live update and its perform RAG task like its handle pdf and docs and we use multiple  librarys:

Phase 1 - Core AI (10-12 Libraries)



Library                  Purpose


langgraph	        AI workflow engine,



langchain	        RAG, tools, prompts



langchain-community	Community integrations



langchain-ollama	Ollama integration



ollama         	        Direct Ollama client (optional)



pydantic                Data validation



python-dotenv   	Environment variables



rich            	Beautiful terminal UI



typer           	CLI commands



loguru          	Logging



| Component       | Technology                       |
| --------------- | -------------------------------- |
| Language        | Python                           |
| Terminal UI     | Rich                             |
| AI Brain        | LangGraph                        |
| LLM             | Ollama                           |
| AI Components   | LangChain                        |
| Config          | Pydantic + python-dotenv         |
| Logging         | Loguru                           |
| Desktop Control | PyAutoGUI + subprocess + psutil  |
| Memory          | SQLite (initially)               |
| Voice           | Faster-Whisper + pyttsx3 (later) |
