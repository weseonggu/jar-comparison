import json
from pathlib import Path
from typing import Any, Dict, List

from src.models.connection_config import ConnectionConfig, ConnectionType
from src.utils import crypto_utils

_CONFIG_DIR = Path.home() / ".jar-comparison"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_raw() -> Dict[str, Any]:
    if not _CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_raw(data: Dict[str, Any]) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_configs() -> List[ConnectionConfig]:
    raw = _load_raw()
    configs = []
    for item in raw.get("connections", []):
        cfg = ConnectionConfig.from_dict(item)
        cfg.password = crypto_utils.decrypt(cfg.password)
        configs.append(cfg)
    return configs


def save_configs(configs: List[ConnectionConfig]) -> None:
    raw = _load_raw()
    serialized = []
    for cfg in configs:
        d = cfg.to_dict()
        d["password"] = crypto_utils.encrypt(d["password"])
        serialized.append(d)
    raw["connections"] = serialized
    _save_raw(raw)


def load_settings() -> Dict[str, Any]:
    raw = _load_raw()
    return raw.get("settings", {})


def save_settings(settings: Dict[str, Any]) -> None:
    raw = _load_raw()
    raw["settings"] = settings
    _save_raw(raw)
