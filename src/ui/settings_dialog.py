from typing import Any, Dict, List

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from src.models.connection_config import ConnectionConfig
from src.ui.connection_panel import ConnectionPanel
from src.utils import config_manager


class SettingsDialog(QDialog):
    """접속 정보 프리셋 관리 및 앱 설정 다이얼로그."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.resize(600, 500)
        self._configs: List[ConnectionConfig] = config_manager.load_configs()
        self._settings: Dict[str, Any] = config_manager.load_settings()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # 프리셋 목록
        preset_group = QGroupBox("접속 정보 프리셋")
        preset_layout = QHBoxLayout(preset_group)

        self._list_widget = QListWidget()
        self._list_widget.currentRowChanged.connect(self._on_select)
        preset_layout.addWidget(self._list_widget, 1)

        btn_col = QVBoxLayout()
        self._btn_add = QPushButton("추가")
        self._btn_save = QPushButton("저장")
        self._btn_delete = QPushButton("삭제")
        self._btn_add.clicked.connect(self._on_add)
        self._btn_save.clicked.connect(self._on_save_preset)
        self._btn_delete.clicked.connect(self._on_delete)
        btn_col.addWidget(self._btn_add)
        btn_col.addWidget(self._btn_save)
        btn_col.addWidget(self._btn_delete)
        btn_col.addStretch()
        preset_layout.addLayout(btn_col)
        layout.addWidget(preset_group)

        # 선택된 프리셋 편집
        edit_group = QGroupBox("프리셋 편집")
        edit_layout = QVBoxLayout(edit_group)
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("이름:"))
        self._name_edit = QLineEdit()
        name_row.addWidget(self._name_edit)
        edit_layout.addLayout(name_row)
        self._conn_panel = ConnectionPanel()
        edit_layout.addWidget(self._conn_panel)
        layout.addWidget(edit_group)

        # 해시 알고리즘 설정
        hash_group = QGroupBox("해시 알고리즘")
        hash_layout = QHBoxLayout(hash_group)
        self._rb_md5 = QRadioButton("MD5")
        self._rb_sha256 = QRadioButton("SHA-256")
        algo = self._settings.get("hash_algo", "MD5")
        if algo == "SHA-256":
            self._rb_sha256.setChecked(True)
        else:
            self._rb_md5.setChecked(True)
        hash_layout.addWidget(self._rb_md5)
        hash_layout.addWidget(self._rb_sha256)
        hash_layout.addStretch()
        layout.addWidget(hash_group)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._on_ok)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _refresh_list(self) -> None:
        self._list_widget.clear()
        for cfg in self._configs:
            self._list_widget.addItem(cfg.name)

    def _on_select(self, row: int) -> None:
        if 0 <= row < len(self._configs):
            cfg = self._configs[row]
            self._name_edit.setText(cfg.name)
            self._conn_panel.set_config(cfg)

    def _on_add(self) -> None:
        new_cfg = ConnectionConfig(name=f"새 프리셋 {len(self._configs) + 1}")
        self._configs.append(new_cfg)
        self._refresh_list()
        self._list_widget.setCurrentRow(len(self._configs) - 1)

    def _on_save_preset(self) -> None:
        row = self._list_widget.currentRow()
        if 0 <= row < len(self._configs):
            cfg = self._conn_panel.get_config()
            cfg.name = self._name_edit.text().strip() or f"프리셋 {row + 1}"
            self._configs[row] = cfg
            self._refresh_list()
            self._list_widget.setCurrentRow(row)

    def _on_delete(self) -> None:
        row = self._list_widget.currentRow()
        if 0 <= row < len(self._configs):
            self._configs.pop(row)
            self._refresh_list()

    def _on_ok(self) -> None:
        config_manager.save_configs(self._configs)
        self._settings["hash_algo"] = "SHA-256" if self._rb_sha256.isChecked() else "MD5"
        config_manager.save_settings(self._settings)
        self.accept()

    def get_configs(self) -> List[ConnectionConfig]:
        return self._configs
