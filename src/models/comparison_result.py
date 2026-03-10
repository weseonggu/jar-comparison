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
    def critical_missing(self) -> List[JarEntry]:
        """누락 파일 중 .java 소스를 제외한 중요 파일 목록."""
        return [e for e in self.missing_in_local if not e.path.endswith(".java")]

    @property
    def source_missing(self) -> List[JarEntry]:
        """누락 파일 중 .java 소스 파일 목록 (낮은 우선순위)."""
        return [e for e in self.missing_in_local if e.path.endswith(".java")]

    @property
    def total_issues(self) -> int:
        """심각도가 높은 문제 수 (.java 소스 누락 제외)."""
        return len(self.critical_missing) + len(self.modified_files)

    @property
    def summary(self) -> str:
        critical = len(self.critical_missing)
        source = len(self.source_missing)
        missing_str = f"누락(운영→로컬): {critical}개"
        if source:
            missing_str += f" (소스 {source}개 별도)"
        return (
            f"{missing_str}  "
            f"변경됨: {len(self.modified_files)}개  "
            f"로컬Only: {len(self.local_only)}개  "
            f"동일: {self.identical_count}개"
        )
