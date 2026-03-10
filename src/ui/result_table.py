from typing import List, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from src.models.jar_entry import JarEntry


class ResultTable(QTableWidget):
    """비교 결과를 표시하는 테이블 위젯."""

    row_double_clicked = pyqtSignal(str)  # 파일 경로 전달

    COLUMNS = ["파일 경로", "운영 크기", "로컬 크기", "상태"]

    COLOR_MISSING = QColor("#FFEAEA")          # 빨강: .class 등 중요 파일 누락
    COLOR_MISSING_SOURCE = QColor("#EBEBEB")   # 회색: .java 소스 파일 누락 (낮은 우선순위)
    COLOR_MODIFIED = QColor("#FFF3CD")
    COLOR_LOCAL = QColor("#E8F5E9")

    def __init__(self, parent=None):
        super().__init__(0, len(self.COLUMNS), parent)
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.doubleClicked.connect(self._on_double_click)

    def _add_row(self, path: str, remote_size: str, local_size: str, status: str, color: QColor) -> None:
        row = self.rowCount()
        self.insertRow(row)
        for col, text in enumerate([path, remote_size, local_size, status]):
            item = QTableWidgetItem(text)
            item.setBackground(color)
            if col == 0:
                item.setData(Qt.ItemDataRole.UserRole, path)
            self.setItem(row, col, item)

    def load_missing(self, entries: List[JarEntry]) -> None:
        self.setRowCount(0)
        # 중요 파일(.class 등) 먼저, .java 소스 파일은 뒤에 표시
        critical = [e for e in entries if not e.path.endswith(".java")]
        source = [e for e in entries if e.path.endswith(".java")]
        for e in critical:
            self._add_row(e.path, e.size_str(), "-", "운영에만 존재", self.COLOR_MISSING)
        for e in source:
            self._add_row(e.path, e.size_str(), "-", "소스만 존재 (참고)", self.COLOR_MISSING_SOURCE)

    def load_modified(self, pairs: List[Tuple[JarEntry, JarEntry]]) -> None:
        self.setRowCount(0)
        for remote_e, local_e in pairs:
            self._add_row(remote_e.path, remote_e.size_str(), local_e.size_str(), "내용 다름", self.COLOR_MODIFIED)

    def load_local_only(self, entries: List[JarEntry]) -> None:
        self.setRowCount(0)
        for e in entries:
            self._add_row(e.path, "-", e.size_str(), "로컬에만 존재", self.COLOR_LOCAL)

    def _on_double_click(self, index) -> None:
        item = self.item(index.row(), 0)
        if item:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                self.row_double_clicked.emit(path)
