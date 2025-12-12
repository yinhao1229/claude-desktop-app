from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.llm_client import LLMClient
from core.markdown import parse_markdown_blocks, render_text_as_html
from core.state import AppState, Message


class CodeBlockWidget(QWidget):
    def __init__(self, code: str):
        super().__init__()
        layout = QVBoxLayout()
        self.code_label = QLabel()
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.setStyleSheet("background-color: #2e2e2e; color: #e6e6e6; font-family: monospace; padding: 8px;")
        self.code_label.setText(render_text_as_html(code))
        copy_button = QPushButton("复制")
        copy_button.clicked.connect(lambda: self.copy_code(code))
        layout.addWidget(copy_button, alignment=Qt.AlignRight)
        layout.addWidget(self.code_label)
        self.setLayout(layout)

    def copy_code(self, code: str) -> None:
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(code)


class MessageBubble(QWidget):
    def __init__(self, message: Message, align_right: bool = False):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignRight if align_right else Qt.AlignLeft)
        bubble = QWidget()
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(8, 8, 8, 8)
        bubble.setLayout(bubble_layout)
        bubble.setStyleSheet(
            "background-color: #f0f0f0; border-radius: 8px;" if align_right else "background-color: #1f2937; color: white; border-radius: 8px;"
        )
        for block_type, content in parse_markdown_blocks(message.content):
            if block_type == "code":
                bubble_layout.addWidget(CodeBlockWidget(content))
            else:
                label = QLabel()
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                label.setText(render_text_as_html(content))
                bubble_layout.addWidget(label)
        layout.addWidget(bubble, alignment=Qt.AlignRight if align_right else Qt.AlignLeft)
        self.setLayout(layout)

    def update_content(self, content: str) -> None:
        self.layout().itemAt(0).widget().deleteLater()
        new_bubble = MessageBubble(Message(role="assistant", content=content), align_right=False)
        self.layout().insertWidget(0, new_bubble.layout().itemAt(0).widget())


class ChatPanel(QWidget):
    def __init__(self, state: AppState, llm_client: LLMClient, on_state_changed: Callable[[], None]):
        super().__init__()
        self.state = state
        self.llm_client = llm_client
        self.on_state_changed = on_state_changed

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.addStretch()
        self.messages_container.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_container)

        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("请输入消息……")
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.on_send_clicked)
        self.send_button.setAutoDefault(True)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addLayout(input_layout)
        self.setLayout(layout)

    def refresh_messages(self) -> None:
        # clear existing message widgets except stretch
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        session = self.state.active_session
        if not session:
            return
        for message in session.messages:
            bubble = MessageBubble(message, align_right=message.role == "user")
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        self.scroll_to_bottom()

    def scroll_to_bottom(self) -> None:
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def set_loading(self, loading: bool) -> None:
        self.state.is_generating = loading
        self.send_button.setEnabled(not loading)
        self.input.setEnabled(not loading)
        if loading:
            self.send_button.setText("生成中…")
        else:
            self.send_button.setText("发送")

    def on_send_clicked(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        if not self.state.active_session:
            QMessageBox.warning(self, "无会话", "请先创建一个会话")
            return
        self.state.add_message("user", text)
        placeholder = self.state.add_message("assistant", "")
        self.refresh_messages()
        self.input.clear()
        self.set_loading(True)
        self.generate_reply()
        self.on_state_changed()

    def append_stream(self, stream: Iterable[str]) -> None:
        assistant_message = self.state.active_session.messages[-1]
        for chunk in stream:
            assistant_message.content += chunk
            self.refresh_messages()
        self.set_loading(False)
        self.on_state_changed()

    def generate_reply(self) -> None:
        session = self.state.active_session
        if not session:
            return
        try:
            stream = self.llm_client.stream(session.messages, system_prompt=session.system_prompt, temperature=session.temperature, max_tokens=session.max_tokens)
            self.append_stream(stream)
        except Exception:
            self.set_loading(False)
            QMessageBox.critical(self, "错误", "从模型获取响应失败")
