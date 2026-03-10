from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from src.models.jar_entry import JarEntry


@dataclass
class ComparisonResult:
    local_jar_path: str
    remote_jar_path: str
    compared_at: datetime = field(default_factory=datetime.now)
    missing_in_local: List[JarEntry] = field(default_factory=list)
    modified_files: List[Tuple[JarEntry, JarEntry]] = field(default_factory=list)
    local_only: List[JarEntry] = field(default_factory=list)
    identical_count: int = 0

    @property
    def total_issues(self) -> int:
        return len(self.missing_in_local) + len(self.modified_files)

    @property
    def summary(self) -> str:
        return (
            f"누락(운영→로컬): {len(self.missing_in_local)}개  "
            f"변경됨: {len(self.modified_files)}개  "
            f"로컬Only: {len(self.local_only)}개  "
            f"동일: {self.identical_count}개"
        )
