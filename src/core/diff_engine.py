import difflib
from typing import List, Tuple

from src.core.jar_reader import read_entry_bytes


class DiffResult:
    def __init__(
        self,
        entry_path: str,
        remote_lines: List[str],
        local_lines: List[str],
        diff_lines: List[str],
        is_binary: bool,
        remote_hex: str = "",
        local_hex: str = "",
    ):
        self.entry_path = entry_path
        self.remote_lines = remote_lines
        self.local_lines = local_lines
        self.diff_lines = diff_lines
        self.is_binary = is_binary
        self.remote_hex = remote_hex
        self.local_hex = local_hex


def _to_hex_dump(data: bytes, bytes_per_row: int = 16) -> str:
    lines = []
    for i in range(0, len(data), bytes_per_row):
        chunk = data[i : i + bytes_per_row]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hex_part:<{bytes_per_row * 3}}  {ascii_part}")
    return "\n".join(lines)


def _is_binary(data: bytes) -> bool:
    try:
        data.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


def compute_diff(
    remote_jar_path: str,
    local_jar_path: str,
    entry_path: str,
    use_hex: bool = False,
) -> DiffResult:
    """두 JAR 파일 내 동일 경로 파일의 Diff를 계산한다."""
    remote_bytes = read_entry_bytes(remote_jar_path, entry_path)
    local_bytes = read_entry_bytes(local_jar_path, entry_path)

    binary = _is_binary(remote_bytes) or _is_binary(local_bytes) or use_hex

    if binary:
        remote_hex = _to_hex_dump(remote_bytes)
        local_hex = _to_hex_dump(local_bytes)
        remote_hex_lines = remote_hex.splitlines(keepends=True)
        local_hex_lines = local_hex.splitlines(keepends=True)
        diff = list(
            difflib.unified_diff(
                remote_hex_lines,
                local_hex_lines,
                fromfile=f"운영/{entry_path}",
                tofile=f"로컬/{entry_path}",
            )
        )
        return DiffResult(
            entry_path=entry_path,
            remote_lines=remote_hex_lines,
            local_lines=local_hex_lines,
            diff_lines=diff,
            is_binary=True,
            remote_hex=remote_hex,
            local_hex=local_hex,
        )
    else:
        remote_text = remote_bytes.decode("utf-8", errors="replace")
        local_text = local_bytes.decode("utf-8", errors="replace")
        remote_lines = remote_text.splitlines(keepends=True)
        local_lines = local_text.splitlines(keepends=True)
        diff = list(
            difflib.unified_diff(
                remote_lines,
                local_lines,
                fromfile=f"운영/{entry_path}",
                tofile=f"로컬/{entry_path}",
            )
        )
        return DiffResult(
            entry_path=entry_path,
            remote_lines=remote_lines,
            local_lines=local_lines,
            diff_lines=diff,
            is_binary=False,
        )
