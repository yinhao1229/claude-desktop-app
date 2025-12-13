from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QMessageBox,
)

from core.state import AppState, Session


class SessionPanel(QWidget):
    session_selected = Signal(str)
    session_deleted = Signal(str)
    session_renamed = Signal(str, str)
    new_session_requested = Signal()

    def __init__(self, state: AppState):
        super().__init__()
        self.state = state

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.setSpacing(6)
        self.list_widget.setAlternatingRowColors(False)

        self.new_button = QPushButton("新建对话")
        self.new_button.clicked.connect(self.new_session_requested)
        self.new_button.setFixedHeight(40)

        title = QLabel("会话")
        title.setObjectName("panelTitle")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(self.new_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def refresh(self) -> None:
        self.list_widget.clear()
        for session in self.state.sessions.values():
            item = QListWidgetItem(session.title)
            item.setData(Qt.UserRole, session.id)
            if session.id == self.state.active_session_id:
                item.setSelected(True)
            self.list_widget.addItem(item)

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        session_id = item.data(Qt.UserRole)
        self.session_selected.emit(session_id)

    def show_context_menu(self, pos) -> None:
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        session_id = item.data(Qt.UserRole)
        menu = QMenu(self)
        rename_action = menu.addAction("重命名")
        delete_action = menu.addAction("删除")
        action = menu.exec_(self.list_widget.mapToGlobal(pos))
        if action == rename_action:
            self.rename_session(session_id)
        elif action == delete_action:
            self.confirm_delete(session_id)

    def rename_session(self, session_id: str) -> None:
        session = self.state.sessions.get(session_id)
        if not session:
            return
        title, ok = QInputDialog.getText(self, "重命名会话", "标题", text=session.title)
        if ok and title:
            self.session_renamed.emit(session_id, title)

    def confirm_delete(self, session_id: str) -> None:
        session = self.state.sessions.get(session_id)
        if not session:
            return
        reply = QMessageBox.question(self, "删除会话", f"确认删除“{session.title}”吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.session_deleted.emit(session_id)
