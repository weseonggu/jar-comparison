from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt

from src.core.diff_engine import DiffResult


class DiffDialog(QDialog):
    """두 JAR 파일 내 동일 경로 파일의 Diff를 좌우로 보여주는 다이얼로그."""

    def __init__(self, diff_result: DiffResult, parent=None):
        super().__init__(parent)
        self.diff_result = diff_result
        self.setWindowTitle(f"Diff: {diff_result.entry_path}")
        self.resize(1100, 650)
        self._build_ui()
        self._populate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        path_label = QLabel(f"<b>파일:</b> {self.diff_result.entry_path}")
        layout.addWidget(path_label)

        if self.diff_result.is_binary:
            note = QLabel("바이너리 파일 — Hex Dump 표시")
            note.setStyleSheet("color: #888; font-size: 11px;")
            layout.addWidget(note)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QVBoxLayout()
        left_label = QLabel("운영 JAR")
        left_label.setStyleSheet("font-weight: bold; color: #c0392b;")
        self._left_edit = QPlainTextEdit()
        self._left_edit.setReadOnly(True)
        self._left_edit.setFont(QFont("Consolas", 9))
        left_widget.addWidget(left_label)
        left_widget.addWidget(self._left_edit)
        left_container = self._make_container(left_widget)

        right_widget = QVBoxLayout()
        right_label = QLabel("로컬 JAR")
        right_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        self._right_edit = QPlainTextEdit()
        self._right_edit.setReadOnly(True)
        self._right_edit.setFont(QFont("Consolas", 9))
        right_widget.addWidget(right_label)
        right_widget.addWidget(self._right_edit)
        right_container = self._make_container(right_widget)

        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setSizes([550, 550])
        layout.addWidget(splitter)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    @staticmethod
    def _make_container(inner_layout) -> "QWidget":
        from PyQt6.QtWidgets import QWidget
        w = QWidget()
        w.setLayout(inner_layout)
        return w

    def _populate(self) -> None:
        dr = self.diff_result

        if dr.is_binary:
            self._left_edit.setPlainText(dr.remote_hex)
            self._right_edit.setPlainText(dr.local_hex)
        else:
            self._left_edit.setPlainText("".join(dr.remote_lines))
            self._right_edit.setPlainText("".join(dr.local_lines))

        # diff 라인 기반으로 변경된 라인 하이라이트 (간단 구현)
        self._highlight_diff(dr.diff_lines)

    def _highlight_diff(self, diff_lines) -> None:
        removed_lines = set()
        added_lines = set()
        remote_idx = 0
        local_idx = 0

        for line in diff_lines:
            if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                continue
            if line.startswith("-"):
                removed_lines.add(remote_idx)
                remote_idx += 1
            elif line.startswith("+"):
                added_lines.add(local_idx)
                local_idx += 1
            else:
                remote_idx += 1
                local_idx += 1

        self._highlight_lines(self._left_edit, removed_lines, QColor("#FFD0D0"))
        self._highlight_lines(self._right_edit, added_lines, QColor("#C8F0C8"))

    @staticmethod
    def _highlight_lines(edit: QPlainTextEdit, line_numbers: set, color: QColor) -> None:
        doc = edit.document()
        for line_no in line_numbers:
            block = doc.findBlockByLineNumber(line_no)
            if not block.isValid():
                continue
            cursor = QTextCursor(block)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            cursor.setCharFormat(fmt)
