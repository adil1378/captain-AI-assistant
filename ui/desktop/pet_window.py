"""
CAPTAIN AI OS 2.0 — NATIVE DESKTOP OVERLAY CONTAINER.
Houses the EXISTING 3D EMO Robot Pet in a native Windows PySide6 container:
- Frameless, transparent, always-on-top window
- Draggable across desktop with mouse tracking
- Full bidirectional bridge with AppRuntime & StateManager
- System Tray controller (Show, Hide, Activate, Standby, Settings, Exit)
- High-risk security confirmation dialog infrastructure
- Graceful headless/CI fallback rendering support
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

from loguru import logger
from app.state import AppState, StateTransitionEvent
from app.runtime import AppRuntime, runtime as global_runtime
from config import settings

# PySide6 imports with graceful fallbacks
try:
    from PySide6.QtCore import Qt, QPoint, QUrl, Signal, QObject, QTimer
    from PySide6.QtGui import QIcon, QAction, QColor, QPainter, QBrush, QPen, QFont, QPixmap
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout,
        QSystemTrayIcon, QMenu, QDialog, QLabel, QPushButton,
        QHBoxLayout, QMessageBox
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineSettings
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False


class StateSignalEmitter(QObject):
    """Qt Signal Emitter for thread-safe state synchronization from async agents."""
    state_changed = Signal(str)
    speech_changed = Signal(bool)
    amplitude_changed = Signal(float)



class SecurityConfirmationDialog(QDialog if PYSIDE_AVAILABLE else object):
    """
    Native PySide6 Security Confirmation Dialog Infrastructure.
    Prompts user for explicit authorization prior to high-risk operations
    (destructive file deletions, system shell execution, OS automation).
    """

    def __init__(self, action_name: str, details: str, risk_level: str = "HIGH", parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.setWindowTitle(f"Security Alert — {action_name}")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 220)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            QLabel {
                color: #c9d1d9;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with Risk Badge
        header_layout = QHBoxLayout()
        title_label = QLabel(f"⚠️ {action_name}")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #58a6ff;")
        header_layout.addWidget(title_label)

        badge_color = "#f85149" if risk_level in ["HIGH", "CRITICAL"] else "#d29922"
        badge_label = QLabel(f"[{risk_level}]")
        badge_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {badge_color};")
        header_layout.addWidget(badge_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Action Details Description
        desc_label = QLabel(details)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 12px; color: #8b949e; margin-top: 8px;")
        layout.addWidget(desc_label)

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        deny_btn = QPushButton("Deny Action")
        deny_btn.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        deny_btn.clicked.connect(self.reject)
        btn_layout.addWidget(deny_btn)

        authorize_btn = QPushButton("Authorize Action")
        authorize_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                border: 1px solid #2ea043;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        authorize_btn.clicked.connect(self.accept)
        btn_layout.addWidget(authorize_btn)

        layout.addLayout(btn_layout)


class CaptainDesktopWindow(QMainWindow if PYSIDE_AVAILABLE else object):
    """
    Windows-Native Desktop Container for the Existing Captain 3D EMO Pet.
    Features:
    - Frameless, translucent background
    - Always-on-top desktop overlay
    - Draggable window
    - Direct AppRuntime state binding
    - System tray management
    """

    def __init__(self, runtime: Optional[AppRuntime] = None):
        if not PYSIDE_AVAILABLE:
            raise RuntimeError("PySide6 is required to initialize CaptainDesktopWindow.")

        super().__init__()
        self.runtime = runtime or global_runtime
        self._drag_pos = QPoint()
        self._emitter = StateSignalEmitter()
        self._emitter.state_changed.connect(self._handle_state_changed_gui)
        self._emitter.speech_changed.connect(self._handle_speech_changed_gui)
        self._emitter.amplitude_changed.connect(self._handle_amplitude_changed_gui)


        self._setup_window_properties()
        self._setup_pet_view()
        self._setup_system_tray()
        self._bind_runtime_state()

        self._voice_manager = None
        if not os.environ.get("PYTEST_CURRENT_TEST"):
            self._init_voice_subsystem()

        logger.info("CaptainDesktopWindow: Desktop container initialized successfully.")

    @property
    def signal_emitter(self) -> StateSignalEmitter:
        """Expose the Qt state signal emitter for testability and external controller hooks."""
        return self._emitter

    def _init_voice_subsystem(self) -> None:
        """Initialize and link the Phase 3 Voice & Clap Manager."""
        try:
            from src.voice.voice_manager import voice_manager
            self._voice_manager = voice_manager
            self._voice_manager.attach_pet_window(self)
            self._voice_manager.start()
            logger.info("CaptainDesktopWindow: Phase 3 Voice subsystem attached and started.")
        except Exception as e:
            logger.warning(f"CaptainDesktopWindow: Voice subsystem init deferred: {e}")


    def _setup_window_properties(self) -> None:
        """Configure native frameless translucent overlay window properties."""
        self.setWindowTitle("Captain AI OS — Desktop Pet")
        self.setFixedSize(340, 380)

        # Frameless, transparent, always-on-top desktop overlay
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        # Position in lower right corner above Windows taskbar by default
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            self.move(geom.width() - 360, geom.height() - 420)

    def _setup_pet_view(self) -> None:
        """Embed the existing Three.js 3D EMO robot pet inside QWebEngineView."""
        central_widget = QWidget(self)
        central_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        html_path = Path(__file__).resolve().parent / "pet.html"

        if WEBENGINE_AVAILABLE and html_path.exists():
            self.web_view = QWebEngineView(central_widget)
            self.web_view.setStyleSheet("background: transparent;")
            self.web_view.page().setBackgroundColor(QColor(0, 0, 0, 0))

            # Enable WebGL & local file access
            web_settings = self.web_view.settings()
            web_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            web_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            web_settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)

            self.web_view.setUrl(QUrl.fromLocalFile(str(html_path)))
            self.web_view.installEventFilter(self)
            layout.addWidget(self.web_view)
            self._using_webengine = True
            logger.info(f"CaptainDesktopWindow: Loaded 3D pet from {html_path}")
        else:
            # High-fidelity QPainter fallback if WebEngine is absent/restricted
            self._using_webengine = False
            self.fallback_label = QLabel(central_widget)
            self.fallback_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.fallback_label)
            self._draw_fallback_pet("happy")
            logger.info("CaptainDesktopWindow: Running in fallback renderer mode.")

        self.setCentralWidget(central_widget)

    def _draw_fallback_pet(self, expression: str = "happy") -> None:
        """Render existing Captain character visually using QPainter when WebEngine is unavailable."""
        pixmap = QPixmap(320, 360)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Head chassis (Dark charcoal #1c1d22)
        painter.setBrush(QBrush(QColor(28, 29, 34)))
        painter.setPen(QPen(QColor(74, 77, 90), 2))
        painter.drawRoundedRect(60, 50, 200, 180, 24, 24)

        # Headphone arch (Purple #4e2a84)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(78, 42, 132), 8))
        painter.drawArc(40, 25, 240, 160, 0 * 16, 180 * 16)

        # Earcups (#22242e) with Cyan LED Rings (#00f2fe)
        painter.setBrush(QBrush(QColor(34, 36, 46)))
        painter.setPen(QPen(QColor(0, 242, 254), 3))
        painter.drawEllipse(35, 110, 32, 55)
        painter.drawEllipse(253, 110, 32, 55)

        # Screen visor bezel (#4a4d5a) and black screen
        painter.setBrush(QBrush(QColor(8, 10, 15)))
        painter.setPen(QPen(QColor(74, 77, 90), 2))
        painter.drawRoundedRect(75, 75, 170, 125, 16, 16)

        # Cyan LED Eyes & Mouth (#00f2fe)
        painter.setBrush(QBrush(QColor(0, 242, 254)))
        painter.setPen(QPen(QColor(0, 242, 254), 2))

        if expression == "thinking":
            # Monocle thinking eye
            painter.drawRoundedRect(95, 110, 45, 45, 12, 12)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(0, 242, 254), 4))
            painter.drawEllipse(165, 105, 45, 45)
        elif expression == "angry":
            # Angry frustrated brows
            painter.drawLine(95, 110, 135, 125)
            painter.drawLine(215, 110, 175, 125)
        elif expression == "sleeping":
            # Sleeping Zzz
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(0, 242, 254), 3))
            painter.drawArc(95, 120, 35, 20, 0 * 16, 180 * 16)
            painter.drawArc(180, 120, 35, 20, 0 * 16, 180 * 16)
        else:
            # Friendly rounded happy eyes
            painter.drawRoundedRect(95, 105, 45, 45, 14, 14)
            painter.drawRoundedRect(175, 105, 45, 45, 14, 14)
            # Smile arc
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(0, 242, 254), 3))
            painter.drawArc(135, 145, 45, 30, 200 * 16, 140 * 16)

        # Feet (#16171d)
        painter.setBrush(QBrush(QColor(22, 23, 29)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(85, 225, 60, 25, 8, 8)
        painter.drawRoundedRect(175, 225, 60, 25, 8, 8)

        # Stage Podium
        painter.setBrush(QBrush(QColor(36, 39, 51)))
        painter.drawRoundedRect(40, 245, 240, 20, 6, 6)

        painter.end()

        if hasattr(self, "fallback_label"):
            self.fallback_label.setPixmap(pixmap)

    def _setup_system_tray(self) -> None:
        """Create Windows System Tray icon with contextual controls."""
        self.tray_icon = QSystemTrayIcon(self)

        # Generate a high-contrast tray icon pixmap
        tray_pixmap = QPixmap(32, 32)
        tray_pixmap.fill(Qt.transparent)
        p = QPainter(tray_pixmap)
        p.setBrush(QBrush(QColor(0, 242, 254)))
        p.setPen(QPen(QColor(30, 144, 255), 2))
        p.drawEllipse(4, 4, 24, 24)
        p.end()
        self.tray_icon.setIcon(QIcon(tray_pixmap))

        # Tray Context Menu
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1f6beb;
                color: #ffffff;
            }
        """)

        show_action = QAction("Show Captain", self)
        show_action.triggered.connect(self.show_pet)
        menu.addAction(show_action)

        hide_action = QAction("Hide Captain", self)
        hide_action.triggered.connect(self.hide_pet)
        menu.addAction(hide_action)

        menu.addSeparator()

        activate_action = QAction("Activate", self)
        activate_action.triggered.connect(lambda: self.runtime.wake("tray_menu"))
        menu.addAction(activate_action)

        deactivate_action = QAction("Deactivate", self)
        deactivate_action.triggered.connect(lambda: self.runtime.sleep("tray_menu"))
        menu.addAction(deactivate_action)

        menu.addSeparator()

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._show_settings_info)
        menu.addAction(settings_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about_info)
        menu.addAction(about_action)

        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.shutdown_app)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _bind_runtime_state(self) -> None:
        """Bind AppRuntime state changes to desktop pet expressions and visibility."""
        def _on_state_transition(event: StateTransitionEvent):
            self._emitter.state_changed.emit(event.to_state.value)

        self.runtime.state_manager.subscribe(_on_state_transition)

    def _handle_state_changed_gui(self, state_str: str) -> None:
        """Update pet appearance in the Qt GUI thread."""
        if state_str == AppState.STANDBY.value:
            # Standby mode: pet enters passive/idle sleeping expression, remains visible (STANDBY != HIDDEN)
            self.set_pet_state(state_str)
        elif state_str == AppState.ACTIVE.value:
            self.set_pet_state(state_str)
        elif state_str == AppState.LISTENING.value:
            self.set_pet_state(state_str)
        elif state_str == AppState.THINKING.value:
            self.set_pet_state(state_str)
        elif state_str == AppState.OBSERVING.value:
            self.set_pet_state(state_str)
        elif state_str == AppState.EXECUTING.value:
            self.set_pet_state(state_str)
        elif state_str == AppState.SPEAKING.value:
            self.set_pet_state(state_str)
            self._set_speaking(True)
        elif state_str == AppState.ERROR.value:
            self.set_pet_state(state_str)

        if state_str != AppState.SPEAKING.value:
            self._set_speaking(False)

    def _handle_speech_changed_gui(self, speaking: bool) -> None:
        """Toggle lip-sync speech mouth flap in the GUI thread."""
        if hasattr(self, "_using_webengine") and self._using_webengine:
            val_js = "true" if speaking else "false"
            self.web_view.page().runJavaScript(f"window.setSpeaking({val_js});")

    def _handle_amplitude_changed_gui(self, amplitude: float) -> None:
        """Forward real-time audio amplitude to WebGL avatar in GUI thread."""
        if hasattr(self, "_using_webengine") and self._using_webengine:
            val = round(min(1.0, max(0.0, amplitude)), 3)
            self.web_view.page().runJavaScript(f"if (window.setAudioAmplitude) window.setAudioAmplitude({val});")


    def set_pet_state(self, state_str: str) -> None:
        """Update pet visual state across all 8 AppState transitions."""
        if hasattr(self, "_using_webengine") and self._using_webengine:
            self.web_view.page().runJavaScript(f"window.setCaptainState('{state_str}');")
        else:
            expr_map = {
                AppState.STANDBY.value: "sleeping",
                AppState.ACTIVE.value: "happy",
                AppState.LISTENING.value: "cool",
                AppState.THINKING.value: "thinking",
                AppState.OBSERVING.value: "star",
                AppState.EXECUTING.value: "salute",
                AppState.SPEAKING.value: "happy",
                AppState.ERROR.value: "angry",
            }
            self._draw_fallback_pet(expr_map.get(state_str, "happy"))

    def update_expression(self, expression: str) -> None:
        """Update pet's facial expression."""
        if hasattr(self, "_using_webengine") and self._using_webengine:
            self.web_view.page().runJavaScript(f"window.setCaptainExpression('{expression}');")
        else:
            self._draw_fallback_pet(expression)

    def eventFilter(self, watched, event):
        """Allow window dragging even when mouse interaction occurs over child QWebEngineView."""
        if PYSIDE_AVAILABLE and hasattr(self, "web_view") and watched == self.web_view:
            if hasattr(event, "type"):
                if event.type() == event.Type.MouseButtonPress and event.button() == Qt.LeftButton:
                    self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                elif event.type() == event.Type.MouseMove and event.buttons() == Qt.LeftButton:
                    self.move(event.globalPosition().toPoint() - self._drag_pos)
        return super().eventFilter(watched, event)

    def _set_speaking(self, speaking: bool) -> None:
        self._emitter.speech_changed.emit(speaking)

    def show_pet(self) -> None:
        """Display the pet overlay window."""
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_pet(self) -> None:
        """Hide the pet overlay window to tray."""
        self.hide()

    def _on_tray_activated(self, reason) -> None:
        """Toggle pet visibility on tray double-click."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide_pet()
            else:
                self.show_pet()

    def _show_settings_info(self) -> None:
        """Show configuration details."""
        QMessageBox.information(
            self,
            "Captain AI OS Settings",
            f"App: {settings.app_name} (v{settings.app_version})\n"
            f"LLM Provider: {settings.llm_provider} ({settings.chat_model})\n"
            f"Ollama URL: {settings.ollama_base_url}\n"
            f"Confirmation Policy: {settings.security_risk_threshold}\n"
            f"Current State: {self.runtime.current_state.value}"
        )

    def _show_about_info(self) -> None:
        """Show About info."""
        QMessageBox.information(
            self,
            "About Captain AI OS",
            "Captain AI OS 2.0\nDesktop-Native Autonomous AI Companion & Agent.\n"
            "Features the authentic 3D EMO Robot Pet with dynamic LED expressions."
        )

    def prompt_confirmation(self, action_name: str, details: str, risk_level: str = "HIGH") -> bool:
        """
        Prompt user for explicit authorization of a sensitive operation.
        Returns True if authorized, False if denied.
        """
        dialog = SecurityConfirmationDialog(action_name, details, risk_level, self)
        return dialog.exec() == QDialog.Accepted

    # Draggable Window Implementation
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def changeEvent(self, event) -> None:
        """Handle window state change: minimize to tray."""
        if PYSIDE_AVAILABLE and hasattr(event, "type") and event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                self.hide_pet()
                event.ignore()
                return
        super().changeEvent(event)

    async def ask_agent(self, query: str, session_id: str = "desktop_session") -> str:
        """Forward user query to the existing Captain AI Agent brain via AppRuntime."""
        return await self.runtime.execute_query(query, session_id=session_id)

    def shutdown_app(self) -> None:
        """Gracefully shutdown Captain AI OS and close overlay window."""
        logger.info("CaptainDesktopWindow: Shutting down desktop container...")
        if self._voice_manager:
            try:
                self._voice_manager.stop()
            except Exception:
                pass
        if self.tray_icon:
            self.tray_icon.hide()
        self.close()
        app = QApplication.instance()
        if app and not os.environ.get("PYTEST_CURRENT_TEST"):
            app.quit()


def launch_desktop_pet(runtime: Optional[AppRuntime] = None) -> int:
    """Entry point to launch the native PySide6 Captain Desktop Pet."""
    if not PYSIDE_AVAILABLE:
        logger.error("PySide6 is not installed. Please install PySide6 to run the desktop companion.")
        return 1

    # High DPI scaling attributes for crisp rendering across high-res displays
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication.instance() or QApplication(sys.argv)
    window = CaptainDesktopWindow(runtime=runtime)
    window.show_pet()
    return app.exec()


if __name__ == "__main__":
    sys.exit(launch_desktop_pet())
