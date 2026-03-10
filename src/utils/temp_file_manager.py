import os
import tempfile
from pathlib import Path


_TEMP_DIR = Path(tempfile.gettempdir()) / "jar-comparison"


def get_temp_dir() -> Path:
    _TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return _TEMP_DIR


def get_temp_path(filename: str) -> str:
    return str(get_temp_dir() / filename)


def cleanup() -> None:
    if _TEMP_DIR.exists():
        for f in _TEMP_DIR.iterdir():
            try:
                f.unlink()
            except Exception:
                pass
