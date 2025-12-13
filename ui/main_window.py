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
            QMainWindow { background-color: #0a0f1a; color: #f1f5f9; }
            QListWidget { background: #0f172a; border: 1px solid #334155; padding: 6px; }
            QListWidget::item { padding: 10px; margin: 4px 2px; border-radius: 8px; color: #e5e7eb; }
            QListWidget::item:selected { background: #2563eb; color: white; }
            QListWidget::item:hover { background: #1e293b; }
            QPushButton { background: #2563eb; color: #f8fafc; border: 1px solid #1d4ed8; padding: 8px 12px; border-radius: 8px; font-weight: 600; }
            QPushButton:hover:!disabled { background: #1d4ed8; }
            QPushButton:disabled { background: #334155; color: #cbd5e1; border-color: #334155; }
            QPushButton#settingsButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #22d3ee, stop:1 #2563eb); border: 1px solid #1d4ed8; padding: 8px 14px; border-radius: 10px; font-weight: 700; }
            QPushButton#settingsButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38e0ff, stop:1 #2e6ff5); color: #f8fafc; }
            QPushButton#settingsButton:pressed { background: #1e40af; padding-top: 9px; padding-bottom: 7px; }
            QPlainTextEdit, QLineEdit, QComboBox { background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 10px; padding: 8px 10px; selection-background-color: #2563eb; selection-color: white; }
            QGroupBox { border: 1px solid #334155; border-radius: 10px; margin-top: 10px; padding: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #cbd5e1; }
            QLabel { color: #e2e8f0; }
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

