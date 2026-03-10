from abc import ABC, abstractmethod
from typing import List

from src.models.connection_config import ConnectionConfig


class RemoteHandler(ABC):
    """운영 서버 접근을 위한 추상 기본 클래스."""

    def __init__(self, config: ConnectionConfig):
        self.config = config

    @abstractmethod
    def test_connection(self) -> bool:
        """접속 테스트. 성공 시 True를 반환한다."""

    @abstractmethod
    def list_jar_files(self) -> List[str]:
        """원격 경로에 있는 JAR 파일 목록을 반환한다."""

    @abstractmethod
    def download_jar(self, remote_filename: str, local_dest_path: str) -> None:
        """원격 JAR 파일을 로컬 경로에 다운로드한다."""

    @abstractmethod
    def close(self) -> None:
        """연결을 종료한다."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
