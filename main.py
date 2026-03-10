import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (패키지 임포트를 위해)
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("JAR Comparison Tool")
    app.setOrganizationName("jar-comparison")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
