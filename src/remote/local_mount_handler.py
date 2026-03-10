import shutil
from pathlib import Path
from typing import List

from src.models.connection_config import ConnectionConfig
from src.remote.base_handler import RemoteHandler


class LocalMountHandler(RemoteHandler):
    """로컬 경로(네트워크 드라이브 마운트 포함)를 통해 파일에 접근한다."""

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)

    def _base_path(self) -> Path:
        return Path(self.config.local_path)

    def test_connection(self) -> bool:
        return self._base_path().is_dir()

    def list_jar_files(self) -> List[str]:
        base = self._base_path()
        if not base.is_dir():
            raise FileNotFoundError(f"경로를 찾을 수 없습니다: {base}")
        return [f.name for f in base.iterdir() if f.suffix.lower() == ".jar"]

    def download_jar(self, remote_filename: str, local_dest_path: str) -> None:
        src = self._base_path() / remote_filename
        shutil.copy2(str(src), local_dest_path)

    def close(self) -> None:
        pass
