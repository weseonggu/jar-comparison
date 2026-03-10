import os
from typing import List

import paramiko

from src.models.connection_config import ConnectionConfig
from src.remote.base_handler import RemoteHandler


class SftpHandler(RemoteHandler):
    """SFTP를 통해 운영 서버에 접근한다."""

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self._ssh: paramiko.SSHClient = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._sftp: paramiko.SFTPClient | None = None

    def _connect(self) -> None:
        kwargs = {
            "hostname": self.config.host,
            "port": self.config.port,
            "username": self.config.username,
            "timeout": 15,
        }
        if self.config.key_file:
            kwargs["key_filename"] = self.config.key_file
        else:
            kwargs["password"] = self.config.password

        self._ssh.connect(**kwargs)
        self._sftp = self._ssh.open_sftp()

    def test_connection(self) -> bool:
        try:
            self._connect()
            return True
        except Exception:
            return False
        finally:
            self.close()

    def list_jar_files(self) -> List[str]:
        if self._sftp is None:
            self._connect()
        remote_path = self.config.remote_path
        items = self._sftp.listdir(remote_path)
        return [f for f in items if f.lower().endswith(".jar")]

    def download_jar(self, remote_filename: str, local_dest_path: str) -> None:
        if self._sftp is None:
            self._connect()
        remote_full = os.path.join(self.config.remote_path, remote_filename).replace("\\", "/")
        self._sftp.get(remote_full, local_dest_path)

    def close(self) -> None:
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None
        try:
            self._ssh.close()
        except Exception:
            pass
