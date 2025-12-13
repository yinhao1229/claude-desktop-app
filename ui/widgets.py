from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtWidgets import QListWidget, QPlainTextEdit, QScrollArea


class AutoHideScrollMixin:
    """Mixin to hide scrollbars until user scrolls with the mouse wheel."""

    def __init__(self, hide_delay_ms: int = 1200) -> None:  # type: ignore[override]
        super().__init__()
        self._hide_delay_ms = hide_delay_ms
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_scrollbars)
        self._hide_scrollbars()

    def _hide_scrollbars(self) -> None:
        if hasattr(self, "setVerticalScrollBarPolicy"):
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]
        if hasattr(self, "setHorizontalScrollBarPolicy"):
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]

    def _show_scrollbars_temporarily(self) -> None:
        if hasattr(self, "setVerticalScrollBarPolicy"):
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # type: ignore[attr-defined]
        if hasattr(self, "setHorizontalScrollBarPolicy"):
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # type: ignore[attr-defined]
        self._hide_timer.start(self._hide_delay_ms)

    def wheelEvent(self, event: QEvent) -> None:  # type: ignore[override]
        self._show_scrollbars_temporarily()
        super().wheelEvent(event)


class AutoHideScrollArea(AutoHideScrollMixin, QScrollArea):
    def __init__(self, parent: Optional[QScrollArea] = None):
        QScrollArea.__init__(self, parent)
        AutoHideScrollMixin.__init__(self)


class AutoHideListWidget(AutoHideScrollMixin, QListWidget):
    def __init__(self, parent: Optional[QListWidget] = None):
        QListWidget.__init__(self, parent)
        AutoHideScrollMixin.__init__(self)


class AutoHidePlainTextEdit(AutoHideScrollMixin, QPlainTextEdit):
    def __init__(self, parent: Optional[QPlainTextEdit] = None):
        QPlainTextEdit.__init__(self, parent)
        AutoHideScrollMixin.__init__(self)

    def enterEvent(self, event: QEvent) -> None:  # type: ignore[override]
        # 鼠标进入输入框时也短暂显示滚动条，便于查看长文本
        self._show_scrollbars_temporarily()
        super().enterEvent(event)
