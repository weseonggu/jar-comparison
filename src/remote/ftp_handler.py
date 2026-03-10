import ftplib
import os
from typing import List

from src.models.connection_config import ConnectionConfig
from src.remote.base_handler import RemoteHandler


class FtpHandler(RemoteHandler):
    """FTP를 통해 운영 서버에 접근한다."""

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self._ftp: ftplib.FTP | None = None

    def _connect(self) -> None:
        self._ftp = ftplib.FTP()
        self._ftp.connect(self.config.host, self.config.port, timeout=15)
        self._ftp.login(self.config.username, self.config.password)
        self._ftp.cwd(self.config.remote_path)

    def test_connection(self) -> bool:
        try:
            self._connect()
            return True
        except Exception:
            return False
        finally:
            self.close()

    def list_jar_files(self) -> List[str]:
        if self._ftp is None:
            self._connect()
        items = self._ftp.nlst()
        return [os.path.basename(f) for f in items if f.lower().endswith(".jar")]

    def download_jar(self, remote_filename: str, local_dest_path: str) -> None:
        if self._ftp is None:
            self._connect()
        with open(local_dest_path, "wb") as f:
            self._ftp.retrbinary(f"RETR {remote_filename}", f.write)

    def close(self) -> None:
        if self._ftp:
            try:
                self._ftp.quit()
            except Exception:
                pass
            self._ftp = None
