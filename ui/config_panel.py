from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
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

        self.model_selector = QComboBox()
        self.model_selector.setPlaceholderText("快速切换预设")
        self.model_input = QLineEdit("mock")
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("例如：https://api.openai.com/v1")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("可填写本地或云端密钥")
        self.api_key_input.setEchoMode(QLineEdit.Password)
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
        form.addRow("快速预设", self.model_selector)
        form.addRow("模型", self.model_input)
        form.addRow("接口 URL", self.api_url_input)
        form.addRow("API Key", self.api_key_input)
        form.addRow("温度", self.temperature_input)
        form.addRow("最大生成 Token", self.max_tokens_input)
        form.addRow("系统提示词", self.system_prompt_input)

        box = QGroupBox("配置")
        box.setLayout(form)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(QLabel("模型与接口"))
        layout.addWidget(box)
        layout.addStretch()
        self.setLayout(layout)

        self.refresh_presets()
        self.model_selector.currentIndexChanged.connect(self.apply_selected_preset)

    def load_session(self) -> None:
        session = self.state.active_session
        if not session:
            return
        self.model_input.setText(session.model)
        self.api_url_input.setText(session.api_url)
        self.api_key_input.setText(session.api_key)
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
        session.model = self.model_input.text().strip() or "mock"
        session.api_url = self.api_url_input.text().strip()
        session.api_key = self.api_key_input.text().strip()

    def refresh_presets(self) -> None:
        self.model_selector.blockSignals(True)
        self.model_selector.clear()
        for preset in self.state.model_presets:
            self.model_selector.addItem(preset.get("name", ""), preset)
        self.model_selector.blockSignals(False)

    def apply_selected_preset(self, index: int) -> None:
        if index < 0:
            return
        preset = self.model_selector.itemData(index)
        if not preset:
            return
        self.model_input.setText(preset.get("model", "mock"))
        self.api_url_input.setText(preset.get("api_url", ""))
        self.api_key_input.setText(preset.get("api_key", ""))
