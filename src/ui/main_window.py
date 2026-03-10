import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

from src.core import jar_comparator
from src.core.diff_engine import compute_diff
from src.models.comparison_result import ComparisonResult
from src.models.connection_config import ConnectionConfig, ConnectionType
from src.remote.ftp_handler import FtpHandler
from src.remote.local_mount_handler import LocalMountHandler
from src.remote.sftp_handler import SftpHandler
from src.ui.connection_panel import ConnectionPanel
from src.ui.diff_dialog import DiffDialog
from src.ui.result_table import ResultTable
from src.ui.settings_dialog import SettingsDialog
from src.utils import config_manager, report_exporter, temp_file_manager


class _DownloadWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, config: ConnectionConfig, jar_filename: str, dest_path: str):
        super().__init__()
        self.config = config
        self.jar_filename = jar_filename
        self.dest_path = dest_path

    def run(self) -> None:
        try:
            self.progress.emit(10, f"운영 서버에서 {self.jar_filename} 다운로드 중...")
            handler = _make_handler(self.config)
            with handler:
                handler.download_jar(self.jar_filename, self.dest_path)
            self.progress.emit(100, "다운로드 완료")
            self.finished.emit(self.dest_path)
        except Exception as e:
            self.error.emit(str(e))


class _CompareWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, local_path: str, remote_path: str):
        super().__init__()
        self.local_path = local_path
        self.remote_path = remote_path

    def run(self) -> None:
        try:
            result = jar_comparator.compare(
                self.local_path,
                self.remote_path,
                progress_callback=lambda pct, msg: self.progress.emit(pct, msg),
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


def _make_handler(config: ConnectionConfig):
    if config.connection_type == ConnectionType.SFTP:
        return SftpHandler(config)
    elif config.connection_type == ConnectionType.FTP:
        return FtpHandler(config)
    else:
        return LocalMountHandler(config)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JAR Comparison Tool")
        self.resize(1200, 750)
        self._result: Optional[ComparisonResult] = None
        self._remote_local_path: Optional[str] = None
        self._worker: Optional[QThread] = None

        self._build_ui()
        self._load_stylesheet()
        self._load_presets()

    def _build_ui(self) -> None:
        # Toolbar
        toolbar = QToolBar("도구")
        self.addToolBar(toolbar)
        self._act_compare = toolbar.addAction("비교 실행 (F5)")
        self._act_compare.setShortcut("F5")
        self._act_compare.triggered.connect(self._start_compare)
        self._act_reset = toolbar.addAction("결과 초기화")
        self._act_reset.triggered.connect(self._reset)
        toolbar.addSeparator()
        self._act_export = toolbar.addAction("리포트 내보내기 (Ctrl+E)")
        self._act_export.setShortcut("Ctrl+E")
        self._act_export.triggered.connect(self._export_report)
        toolbar.addSeparator()
        self._act_settings = toolbar.addAction("설정")
        self._act_settings.triggered.connect(self._open_settings)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # 상단: 로컬 JAR 선택 + 운영 JAR 접속
        top_row = QHBoxLayout()

        # 로컬 JAR 패널
        local_group = QGroupBox("로컬 JAR")
        local_layout = QVBoxLayout(local_group)
        self._local_path_edit = QLineEdit()
        self._local_path_edit.setPlaceholderText("로컬 빌드 JAR 파일 경로")
        self._local_path_edit.setReadOnly(True)
        local_browse = QPushButton("파일 선택")
        local_browse.clicked.connect(self._browse_local_jar)
        local_layout.addWidget(self._local_path_edit)
        local_layout.addWidget(local_browse)
        top_row.addWidget(local_group, 1)

        # 운영 JAR 패널
        remote_group = QGroupBox("운영 JAR")
        remote_layout = QVBoxLayout(remote_group)

        # 프리셋 선택
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("프리셋:"))
        self._preset_combo = QComboBox()
        self._preset_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        preset_row.addWidget(self._preset_combo)
        remote_layout.addLayout(preset_row)

        self._conn_panel = ConnectionPanel()
        remote_layout.addWidget(self._conn_panel)

        # JAR 파일 선택 (운영)
        jar_row = QHBoxLayout()
        jar_row.addWidget(QLabel("JAR 파일:"))
        self._remote_jar_combo = QComboBox()
        self._remote_jar_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._btn_list_jars = QPushButton("목록 조회")
        self._btn_list_jars.clicked.connect(self._list_remote_jars)
        self._btn_test_conn = QPushButton("접속 테스트")
        self._btn_test_conn.clicked.connect(self._test_connection)
        jar_row.addWidget(self._remote_jar_combo)
        jar_row.addWidget(self._btn_list_jars)
        jar_row.addWidget(self._btn_test_conn)
        remote_layout.addLayout(jar_row)

        top_row.addWidget(remote_group, 2)
        root.addLayout(top_row)

        # 탭 결과
        self._tab_widget = QTabWidget()
        self._tab_missing = ResultTable()
        self._tab_modified = ResultTable()
        self._tab_local_only = ResultTable()
        self._tab_widget.addTab(self._tab_missing, "누락 파일 (운영→로컬)  0")
        self._tab_widget.addTab(self._tab_modified, "변경된 파일  0")
        self._tab_widget.addTab(self._tab_local_only, "로컬 Only  0")
        root.addWidget(self._tab_widget)

        self._tab_missing.row_double_clicked.connect(self._open_diff_missing)
        self._tab_modified.row_double_clicked.connect(self._open_diff)

        # 상태바
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedWidth(250)
        self._progress_bar.setVisible(False)
        self._status_bar.addPermanentWidget(self._progress_bar)
        self._status_label = QLabel("준비")
        self._status_bar.addWidget(self._status_label)

    def _load_stylesheet(self) -> None:
        qss_path = Path(__file__).parent / "resources" / "styles" / "main.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    def _load_presets(self) -> None:
        self._presets = config_manager.load_configs()
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItem("(직접 입력)")
        for cfg in self._presets:
            self._preset_combo.addItem(cfg.name)
        self._preset_combo.blockSignals(False)

    def _on_preset_selected(self, index: int) -> None:
        if index > 0 and index - 1 < len(self._presets):
            self._conn_panel.set_config(self._presets[index - 1])

    def _browse_local_jar(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "로컬 JAR 선택", "", "JAR 파일 (*.jar);;모든 파일 (*)")
        if path:
            self._local_path_edit.setText(path)

    def _test_connection(self) -> None:
        cfg = self._conn_panel.get_config()
        self._set_status(0, "접속 테스트 중...")
        handler = _make_handler(cfg)
        if handler.test_connection():
            QMessageBox.information(self, "접속 테스트", "접속 성공!")
        else:
            QMessageBox.warning(self, "접속 테스트", "접속 실패. 설정을 확인하세요.")
        self._set_status(0, "준비")

    def _list_remote_jars(self) -> None:
        cfg = self._conn_panel.get_config()
        try:
            self._set_status(0, "JAR 목록 조회 중...")
            handler = _make_handler(cfg)
            with handler:
                jars = handler.list_jar_files()
            self._remote_jar_combo.clear()
            for jar in sorted(jars):
                self._remote_jar_combo.addItem(jar)
            self._set_status(0, f"JAR {len(jars)}개 조회 완료")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"JAR 목록 조회 실패:\n{e}")
            self._set_status(0, "오류")

    def _start_compare(self) -> None:
        local_path = self._local_path_edit.text().strip()
        if not local_path or not Path(local_path).is_file():
            QMessageBox.warning(self, "경고", "로컬 JAR 파일을 선택하세요.")
            return

        remote_jar_name = self._remote_jar_combo.currentText().strip()
        if not remote_jar_name:
            QMessageBox.warning(self, "경고", "운영 JAR 파일을 선택하세요.\n먼저 [목록 조회]를 눌러주세요.")
            return

        cfg = self._conn_panel.get_config()
        dest = temp_file_manager.get_temp_path(f"remote_{remote_jar_name}")

        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._act_compare.setEnabled(False)

        self._download_worker = _DownloadWorker(cfg, remote_jar_name, dest)
        self._download_worker.progress.connect(self._set_status)
        self._download_worker.finished.connect(lambda path: self._run_compare(local_path, path))
        self._download_worker.error.connect(self._on_error)
        self._download_worker.start()

    def _run_compare(self, local_path: str, remote_local_path: str) -> None:
        self._remote_local_path = remote_local_path
        self._compare_worker = _CompareWorker(local_path, remote_local_path)
        self._compare_worker.progress.connect(self._set_status)
        self._compare_worker.finished.connect(self._on_compare_done)
        self._compare_worker.error.connect(self._on_error)
        self._compare_worker.start()

    def _on_compare_done(self, result: ComparisonResult) -> None:
        self._result = result
        self._tab_missing.load_missing(result.missing_in_local)
        self._tab_modified.load_modified(result.modified_files)
        self._tab_local_only.load_local_only(result.local_only)

        critical_missing = [e for e in result.missing_in_local if not e.path.endswith(".java")]
        source_missing = [e for e in result.missing_in_local if e.path.endswith(".java")]
        missing_label = f"누락 파일 (운영→로컬)  {len(critical_missing)}건"
        if source_missing:
            missing_label += f"  +소스 {len(source_missing)}건"
        self._tab_widget.setTabText(0, missing_label)
        self._tab_widget.setTabText(1, f"변경된 파일  {len(result.modified_files)}")
        self._tab_widget.setTabText(2, f"로컬 Only  {len(result.local_only)}")

        self._progress_bar.setVisible(False)
        self._act_compare.setEnabled(True)
        self._status_label.setText(result.summary)

        if result.total_issues > 0:
            QMessageBox.warning(
                self,
                "비교 완료",
                f"문제가 발견되었습니다!\n{result.summary}",
            )
        else:
            QMessageBox.information(self, "비교 완료", f"이상 없음.\n{result.summary}")

    def _on_error(self, msg: str) -> None:
        self._progress_bar.setVisible(False)
        self._act_compare.setEnabled(True)
        self._status_label.setText("오류 발생")
        QMessageBox.critical(self, "오류", msg)

    def _set_status(self, pct: int, msg: str) -> None:
        self._status_label.setText(msg)
        if pct > 0:
            self._progress_bar.setValue(pct)

    def _reset(self) -> None:
        self._result = None
        self._remote_local_path = None
        self._tab_missing.setRowCount(0)
        self._tab_modified.setRowCount(0)
        self._tab_local_only.setRowCount(0)
        self._tab_widget.setTabText(0, "누락 파일 (운영→로컬)  0")
        self._tab_widget.setTabText(1, "변경된 파일  0")
        self._tab_widget.setTabText(2, "로컬 Only  0")
        self._progress_bar.setVisible(False)
        self._status_label.setText("준비")

    def _open_diff(self, entry_path: str) -> None:
        if not self._result:
            return
        local_jar = self._result.local_jar_path
        remote_jar = self._result.remote_jar_path
        try:
            diff = compute_diff(remote_jar, local_jar, entry_path)
            dlg = DiffDialog(diff, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"Diff 생성 실패:\n{e}")

    def _open_diff_missing(self, entry_path: str) -> None:
        QMessageBox.information(
            self,
            "누락 파일",
            f"이 파일은 운영 JAR에만 존재합니다:\n{entry_path}\n\nDiff를 표시할 수 없습니다.",
        )

    def _export_report(self) -> None:
        if not self._result:
            QMessageBox.warning(self, "경고", "먼저 비교를 실행하세요.")
            return

        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "리포트 저장",
            "jar_comparison_report",
            "HTML 파일 (*.html);;CSV 파일 (*.csv)",
        )
        if not path:
            return

        try:
            if "html" in selected_filter.lower() or path.endswith(".html"):
                if not path.endswith(".html"):
                    path += ".html"
                report_exporter.export_html(self._result, path)
            else:
                if not path.endswith(".csv"):
                    path += ".csv"
                report_exporter.export_csv(self._result, path)
            QMessageBox.information(self, "완료", f"리포트 저장 완료:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"리포트 저장 실패:\n{e}")

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self)
        if dlg.exec():
            self._load_presets()

    def closeEvent(self, event) -> None:
        temp_file_manager.cleanup()
        super().closeEvent(event)
