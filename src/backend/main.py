import sys
from pathlib import Path

# Ensure project root (D:\captain) is in sys.path regardless of execution CWD
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.backend.config import settings
from src.backend.api.v1.router import api_v1_router
from src.backend.core.event_bus import event_bus

# Configure Loguru
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:5}</level> | <cyan>{name}:{line}</cyan> - <level>{message}</level>"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    await event_bus.publish("ServerStarted", "MainServer", {"version": settings.APP_VERSION})
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")
    await event_bus.publish("ServerShutdown", "MainServer", {})


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Captain AI OS — Enterprise Multi-Agent Desktop AI Operating System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Register API routes FIRST so /api/v1 is prioritized over static fallback
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

# Resolve path to ui/web/
_web_ui_path = Path(__file__).parent.parent.parent / "ui" / "web"
if not _web_ui_path.exists():
    _web_ui_path = Path("./ui/web").resolve()

# Mount generated output media files (e.g. AI images)
_outputs_path = _PROJECT_ROOT / "data" / "outputs"
_outputs_path.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(_outputs_path)), name="outputs")
logger.info(f"Media outputs mounted at /outputs from {_outputs_path}")

from fastapi.responses import RedirectResponse

@app.get("/ui", include_in_schema=False)
async def redirect_ui():
    return RedirectResponse(url="/ui/")

if _web_ui_path.exists():
    # Mount /ui/
    app.mount("/ui", StaticFiles(directory=str(_web_ui_path), html=True), name="web_ui")
    # Mount / so root http://127.0.0.1:8000/ serves index.html and style.css directly
    app.mount("/", StaticFiles(directory=str(_web_ui_path), html=True), name="web_root")
    logger.info(f"Web UI mounted at / and /ui/ from {_web_ui_path}")
else:
    logger.warning(f"Web UI path not found: {_web_ui_path}")


def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    uvicorn.run("src.backend.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    start_server()
