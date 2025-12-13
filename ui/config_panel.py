from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.state import AppState


class ConfigPanel(QWidget):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state

        self.setMinimumWidth(280)

        self.model_input = QLineEdit("mock")
        self.temperature_input = QLineEdit("1.0")
        self.max_tokens_input = QSpinBox()
        self.max_tokens_input.setRange(1, 16384)
        self.max_tokens_input.setSpecialValueText("无")
        self.max_tokens_input.setValue(0)
        self.system_prompt_input = QPlainTextEdit()
        self.system_prompt_input.setPlaceholderText("为当前会话设置的系统提示语……")
        self.system_prompt_input.setMinimumHeight(140)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)
        form.addRow("模型", self.model_input)
        form.addRow("温度", self.temperature_input)
        form.addRow("最大生成 Token", self.max_tokens_input)
        form.addRow("系统提示词", self.system_prompt_input)

        box = QGroupBox("配置")
        box.setLayout(form)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(box)
        layout.addStretch()
        self.setLayout(layout)

    def load_session(self) -> None:
        session = self.state.active_session
        if not session:
            return
        self.temperature_input.setText(str(session.temperature))
        self.system_prompt_input.setPlainText(session.system_prompt)
        self.max_tokens_input.setValue(session.max_tokens or 0)

    def save_session(self) -> None:
        session = self.state.active_session
        if not session:
            return
        try:
            session.temperature = float(self.temperature_input.text() or "1.0")
        except ValueError:
            session.temperature = 1.0
        session.system_prompt = self.system_prompt_input.toPlainText()
        session.max_tokens = self.max_tokens_input.value() or None
