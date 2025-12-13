from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter

from core.llm_client import MockLLMClient
from core.state import AppState
from core.storage import save_state
from ui.chat_panel import ChatPanel
from ui.config_panel import ConfigPanel
from ui.session_panel import SessionPanel


class MainWindow(QMainWindow):
    def __init__(self, state: AppState, storage_path: Path):
        super().__init__()
        self.state = state
        self.storage_path = storage_path
        self.llm_client = MockLLMClient()

        self.setWindowTitle("Cherry 风格聊天")
        self.resize(1200, 800)

        self.setStyleSheet(
            """
            QMainWindow { background-color: #0b1221; color: #e5e7eb; }
            QListWidget { background: #0f172a; border: 1px solid #1f2937; padding: 6px; }
            QListWidget::item { padding: 10px; margin: 4px 2px; border-radius: 8px; color: #e5e7eb; }
            QListWidget::item:selected { background: #1d4ed8; color: white; }
            QPushButton { background: #1d4ed8; color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 600; }
            QPushButton:hover:!disabled { background: #2563eb; }
            QPushButton:disabled { background: #334155; color: #cbd5e1; }
            QPlainTextEdit { background: #0b1221; color: #e5e7eb; border: 1px solid #1f2937; border-radius: 10px; padding: 10px; }
            QGroupBox { border: 1px solid #1f2937; border-radius: 10px; margin-top: 10px; padding: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #9ca3af; }
            QLabel { color: #e5e7eb; }
            QScrollArea { border: none; }
            QFormLayout > * { color: #e5e7eb; }
            """
        )

        self.session_panel = SessionPanel(self.state)
        self.session_panel.session_selected.connect(self.on_session_selected)
        self.session_panel.session_deleted.connect(self.on_session_deleted)
        self.session_panel.session_renamed.connect(self.on_session_renamed)
        self.session_panel.new_session_requested.connect(self.on_new_session)

        self.chat_panel = ChatPanel(self.state, self.llm_client, on_state_changed=self.persist_state)
        self.config_panel = ConfigPanel(self.state)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.session_panel)
        splitter.addWidget(self.chat_panel)
        splitter.addWidget(self.config_panel)
        splitter.setSizes([200, 700, 300])
        splitter.setHandleWidth(2)
        self.setCentralWidget(splitter)

        if not self.state.sessions:
            self.state.create_session()
        self.refresh_all()

    def refresh_all(self) -> None:
        self.session_panel.refresh()
        self.chat_panel.refresh_messages()
        self.config_panel.load_session()

    def persist_state(self) -> None:
        self.config_panel.save_session()
        save_state(self.state, str(self.storage_path))

    def on_session_selected(self, session_id: str) -> None:
        self.config_panel.save_session()
        self.state.set_active_session(session_id)
        self.refresh_all()
        self.persist_state()

    def on_session_deleted(self, session_id: str) -> None:
        self.config_panel.save_session()
        self.state.delete_session(session_id)
        self.refresh_all()
        self.persist_state()

    def on_session_renamed(self, session_id: str, title: str) -> None:
        self.state.rename_session(session_id, title)
        self.refresh_all()
        self.persist_state()

    def on_new_session(self) -> None:
        self.config_panel.save_session()
        self.state.create_session()
        self.refresh_all()
        self.persist_state()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.config_panel.save_session()
        self.persist_state()
        event.accept()


def run_app(state: AppState, storage_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(state, storage_path)
    window.show()
    app.exec()

