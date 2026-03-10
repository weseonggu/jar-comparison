from dataclasses import dataclass, field
from enum import Enum


class ConnectionType(Enum):
    SFTP = "SFTP"
    FTP = "FTP"
    LOCAL = "LOCAL"


@dataclass
class ConnectionConfig:
    name: str = "기본 설정"
    connection_type: ConnectionType = ConnectionType.SFTP
    host: str = ""
    port: int = 22
    username: str = ""
    password: str = ""
    key_file: str = ""
    remote_path: str = "/WEB-INF/lib/"
    local_path: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "connection_type": self.connection_type.value,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "key_file": self.key_file,
            "remote_path": self.remote_path,
            "local_path": self.local_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConnectionConfig":
        obj = cls()
        obj.name = data.get("name", "기본 설정")
        obj.connection_type = ConnectionType(data.get("connection_type", "SFTP"))
        obj.host = data.get("host", "")
        obj.port = data.get("port", 22)
        obj.username = data.get("username", "")
        obj.password = data.get("password", "")
        obj.key_file = data.get("key_file", "")
        obj.remote_path = data.get("remote_path", "/WEB-INF/lib/")
        obj.local_path = data.get("local_path", "")
        return obj
