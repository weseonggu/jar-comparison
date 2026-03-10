from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.models.connection_config import ConnectionConfig, ConnectionType


class ConnectionPanel(QWidget):
    """운영 서버 접속 방식을 선택하고 접속 정보를 입력하는 패널."""

    config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # 접속 방식 선택
        type_box = QGroupBox("접속 방식")
        type_layout = QHBoxLayout(type_box)
        self._rb_sftp = QRadioButton("SFTP")
        self._rb_ftp = QRadioButton("FTP")
        self._rb_local = QRadioButton("로컬 경로")
        self._rb_sftp.setChecked(True)
        type_layout.addWidget(self._rb_sftp)
        type_layout.addWidget(self._rb_ftp)
        type_layout.addWidget(self._rb_local)
        root.addWidget(type_box)

        # 네트워크 접속 정보
        self._network_group = QGroupBox("서버 정보")
        form = QFormLayout(self._network_group)
        self._host_edit = QLineEdit()
        self._host_edit.setPlaceholderText("192.168.0.1")
        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(22)
        self._user_edit = QLineEdit()
        self._pass_edit = QLineEdit()
        self._pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._remote_path_edit = QLineEdit()
        self._remote_path_edit.setText("/WEB-INF/lib/")
        self._key_file_edit = QLineEdit()
        self._key_file_edit.setPlaceholderText("(선택) SSH 키 파일 경로")
        key_btn = QPushButton("찾아보기")
        key_btn.setFixedWidth(80)
        key_btn.clicked.connect(self._browse_key_file)

        key_row = QWidget()
        key_row_layout = QHBoxLayout(key_row)
        key_row_layout.setContentsMargins(0, 0, 0, 0)
        key_row_layout.addWidget(self._key_file_edit)
        key_row_layout.addWidget(key_btn)

        form.addRow("호스트:", self._host_edit)
        form.addRow("포트:", self._port_spin)
        form.addRow("사용자명:", self._user_edit)
        form.addRow("비밀번호:", self._pass_edit)
        form.addRow("원격 경로:", self._remote_path_edit)
        form.addRow("키 파일:", key_row)
        root.addWidget(self._network_group)

        # 로컬 경로 입력
        self._local_group = QGroupBox("로컬 경로")
        local_layout = QHBoxLayout(self._local_group)
        self._local_path_edit = QLineEdit()
        self._local_path_edit.setPlaceholderText("예: Z:\\WEB-INF\\lib")
        browse_btn = QPushButton("찾아보기")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_local)
        local_layout.addWidget(self._local_path_edit)
        local_layout.addWidget(browse_btn)
        root.addWidget(self._local_group)
        self._local_group.setVisible(False)

        # 라디오 버튼 이벤트
        self._rb_sftp.toggled.connect(self._on_type_changed)
        self._rb_ftp.toggled.connect(self._on_type_changed)
        self._rb_local.toggled.connect(self._on_type_changed)

    def _on_type_changed(self) -> None:
        is_local = self._rb_local.isChecked()
        self._network_group.setVisible(not is_local)
        self._local_group.setVisible(is_local)
        if self._rb_sftp.isChecked():
            self._port_spin.setValue(22)
        elif self._rb_ftp.isChecked():
            self._port_spin.setValue(21)
        self.config_changed.emit()

    def _browse_key_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "SSH 키 파일 선택", "", "키 파일 (*.pem *.ppk *);;모든 파일 (*)")
        if path:
            self._key_file_edit.setText(path)

    def _browse_local(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "JAR 디렉토리 선택")
        if path:
            self._local_path_edit.setText(path)

    def get_config(self) -> ConnectionConfig:
        cfg = ConnectionConfig()
        if self._rb_sftp.isChecked():
            cfg.connection_type = ConnectionType.SFTP
        elif self._rb_ftp.isChecked():
            cfg.connection_type = ConnectionType.FTP
        else:
            cfg.connection_type = ConnectionType.LOCAL

        cfg.host = self._host_edit.text().strip()
        cfg.port = self._port_spin.value()
        cfg.username = self._user_edit.text().strip()
        cfg.password = self._pass_edit.text()
        cfg.remote_path = self._remote_path_edit.text().strip()
        cfg.key_file = self._key_file_edit.text().strip()
        cfg.local_path = self._local_path_edit.text().strip()
        return cfg

    def set_config(self, cfg: ConnectionConfig) -> None:
        if cfg.connection_type == ConnectionType.SFTP:
            self._rb_sftp.setChecked(True)
        elif cfg.connection_type == ConnectionType.FTP:
            self._rb_ftp.setChecked(True)
        else:
            self._rb_local.setChecked(True)

        self._host_edit.setText(cfg.host)
        self._port_spin.setValue(cfg.port)
        self._user_edit.setText(cfg.username)
        self._pass_edit.setText(cfg.password)
        self._remote_path_edit.setText(cfg.remote_path)
        self._key_file_edit.setText(cfg.key_file)
        self._local_path_edit.setText(cfg.local_path)
