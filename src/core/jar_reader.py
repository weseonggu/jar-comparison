import hashlib
import zipfile
from pathlib import Path
from typing import Dict

from src.models.jar_entry import JarEntry


def extract_entries(jar_path: str) -> Dict[str, JarEntry]:
    """JAR(ZIP) 파일에서 내부 엔트리 목록을 추출한다."""
    entries: Dict[str, JarEntry] = {}
    with zipfile.ZipFile(jar_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            entries[info.filename] = JarEntry(
                path=info.filename,
                size=info.file_size,
                crc=info.CRC,
                compress_type=info.compress_type,
            )
    return entries


def compute_md5(jar_path: str, entry_path: str) -> str:
    """JAR 내부의 특정 파일에 대해 MD5 해시를 계산한다."""
    with zipfile.ZipFile(jar_path, "r") as zf:
        data = zf.read(entry_path)
    return hashlib.md5(data).hexdigest()


def read_entry_bytes(jar_path: str, entry_path: str) -> bytes:
    """JAR 내부의 특정 파일의 바이트를 반환한다."""
    with zipfile.ZipFile(jar_path, "r") as zf:
        return zf.read(entry_path)
