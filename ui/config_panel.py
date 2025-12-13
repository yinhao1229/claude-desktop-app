from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStyle,
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

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        title_label = QLabel("模型与接口")
        title_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        self.settings_button = QPushButton("设置")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.setToolTip("添加或编辑自定义模型预设")
        self.settings_button.clicked.connect(self.open_custom_model_dialog)
        header_row.addWidget(title_label)
        header_row.addStretch()
        header_row.addWidget(self.settings_button)

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
        layout.addLayout(header_row)
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

    def open_custom_model_dialog(self) -> None:
        dialog = CustomModelDialog(self.state.model_presets, self)
        if dialog.exec() == QDialog.Accepted:
            preset = dialog.get_preset()
            existing = next((p for p in self.state.model_presets if p.get("name") == preset.get("name")), None)
            if existing:
                existing.update(preset)
            else:
                self.state.model_presets.append(preset)
            self.refresh_presets()
            self.model_selector.setCurrentIndex(self.model_selector.count() - 1)
            self.apply_selected_preset(self.model_selector.currentIndex())


class CustomModelDialog(QDialog):
    def __init__(self, presets: list[dict[str, str]], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("自定义模型设置")
        self.setModal(True)
        self.setFixedWidth(420)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("显示名称，例如：内部测试模型")
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("模型 ID，例如：gpt-4o-mini")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("接口地址")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("密钥（可选）")
        self.key_input.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("名称", self.name_input)
        form.addRow("模型", self.model_input)
        form.addRow("接口 URL", self.url_input)
        form.addRow("API Key", self.key_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addWidget(buttons, alignment=Qt.AlignRight)
        self.setLayout(layout)

        if presets:
            last = presets[-1]
            self.name_input.setText(last.get("name", ""))
            self.model_input.setText(last.get("model", ""))
            self.url_input.setText(last.get("api_url", ""))
            self.key_input.setText(last.get("api_key", ""))

    def get_preset(self) -> dict[str, str]:
        return {
            "name": self.name_input.text().strip() or "自定义模型",
            "model": self.model_input.text().strip() or "mock",
            "api_url": self.url_input.text().strip(),
            "api_key": self.key_input.text().strip(),
        }
