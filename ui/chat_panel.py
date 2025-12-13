from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.code_label = QLabel()
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.setStyleSheet(
            "background-color: #0f172a; color: #e6e6e6; font-family: 'JetBrains Mono', 'Cascadia Code', monospace;"
            "padding: 10px; border: 1px solid #1f2937; border-radius: 10px;"
        )
        self.code_label.setText(render_text_as_html(code))
        copy_button = QPushButton("复制代码")
        copy_button.setFixedWidth(90)
        copy_button.clicked.connect(lambda: self.copy_code(code))
        copy_button.setStyleSheet("padding: 6px 10px; font-weight: 600;")

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
        self.align_right = align_right

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignRight if align_right else Qt.AlignLeft)
        layout.setContentsMargins(2, 4, 2, 4)

        self.bubble = QWidget()
        self.bubble.setMaximumWidth(780)
        self.bubble_layout = QVBoxLayout()
        self.bubble_layout.setContentsMargins(14, 10, 14, 12)
        self.bubble_layout.setSpacing(8)
        self.bubble.setLayout(self.bubble_layout)
        self.bubble.setStyleSheet(
            "background-color: #1d4ed8; color: white; border-radius: 12px;"
            if align_right
            else "background-color: #0f172a; color: #e5e7eb; border: 1px solid #1f2937; border-radius: 12px;"
        )

        self.render_content(message.content)
        layout.addWidget(self.bubble, alignment=Qt.AlignRight if align_right else Qt.AlignLeft)
        self.setLayout(layout)

    def render_content(self, content: str) -> None:
        while self.bubble_layout.count():
            item = self.bubble_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for block_type, text in parse_markdown_blocks(content):
            if block_type == "code":
                self.bubble_layout.addWidget(CodeBlockWidget(text))
            else:
                label = QLabel()
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                label.setWordWrap(True)
                label.setText(render_text_as_html(text))
                label.setStyleSheet("font-size: 14px; line-height: 1.5;")
                self.bubble_layout.addWidget(label)

    def update_content(self, content: str) -> None:
        self.render_content(content)


class SendTextEdit(QPlainTextEdit):
    send_requested = Signal()

    def keyPressEvent(self, event):  # type: ignore[override]
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.send_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class ChatPanel(QWidget):
    def __init__(self, state: AppState, llm_client: LLMClient, on_state_changed: Callable[[], None]):
        super().__init__()
        self.state = state
        self.llm_client = llm_client
        self.on_state_changed = on_state_changed
        self.message_widgets: list[MessageBubble] = []

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: #0b1221;")
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(24, 16, 24, 24)
        self.messages_layout.setSpacing(14)
        self.messages_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.messages_container.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_container)

        self.input = SendTextEdit()
        self.input.setPlaceholderText("请输入消息，按 Enter 发送")
        self.input.setMinimumHeight(48)
        self.input.setMaximumHeight(80)
        self.input.setFrameStyle(QFrame.NoFrame)
        self.input.setStyleSheet(
            "QPlainTextEdit { padding: 10px 6px; font-size: 14px; border: none; color: #e5e7eb;"
            " background: transparent; }"
            "QPlainTextEdit:disabled { color: #94a3b8; }"
        )
        self.input.send_requested.connect(self.on_send_clicked)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.on_send_clicked)
        self.send_button.setAutoDefault(True)
        self.send_button.setMinimumHeight(40)
        self.send_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.send_button.setStyleSheet(
            "QPushButton { background: #1d4ed8; color: white; border: none; border-radius: 10px;"
            " padding: 10px 16px; font-weight: 700; }"
            "QPushButton:hover { background: #265ee8; }"
            "QPushButton:pressed { background: #1940a9; }"
            "QPushButton:disabled { background: #334155; color: #cbd5e1; }"
        )

        input_inner_layout = QHBoxLayout()
        input_inner_layout.setContentsMargins(14, 10, 12, 10)
        input_inner_layout.setSpacing(12)
        input_inner_layout.addWidget(self.input, stretch=8)
        input_inner_layout.addWidget(self.send_button, stretch=2, alignment=Qt.AlignRight | Qt.AlignVCenter)

        self.input_container = QWidget()
        self.input_container.setObjectName("inputContainer")
        self.input_container.setLayout(input_inner_layout)
        self.input_container.setMinimumHeight(60)
        self.input_container.setStyleSheet(
            "QWidget#inputContainer { background: #0d1628; border: 1.5px solid #1f2937; border-radius: 12px; }"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.input_container)
        self.setLayout(layout)

    def refresh_messages(self) -> None:
        # clear existing message widgets except stretch
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.message_widgets.clear()
        session = self.state.active_session
        if not session:
            return
        for message in session.messages:
            bubble = MessageBubble(message, align_right=message.role == "user")
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
            self.message_widgets.append(bubble)
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
            if self.message_widgets:
                self.message_widgets[-1].update_content(assistant_message.content)
            else:
                self.refresh_messages()
            QApplication.processEvents()
            self.scroll_to_bottom()
        self.set_loading(False)
        self.on_state_changed()

    def generate_reply(self) -> None:
        session = self.state.active_session
        if not session:
            return
        try:
            stream = self.llm_client.stream(
                session.messages,
                system_prompt=session.system_prompt,
                temperature=session.temperature,
                max_tokens=session.max_tokens,
                api_url=session.api_url,
                api_key=session.api_key,
                model=session.model,
            )
            self.append_stream(stream)
        except Exception:
            self.set_loading(False)
            QMessageBox.critical(self, "错误", "从模型获取响应失败")
