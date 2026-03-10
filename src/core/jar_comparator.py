from datetime import datetime
from typing import Callable, Optional

from src.core.jar_reader import compute_md5, extract_entries
from src.models.comparison_result import ComparisonResult
from src.models.jar_entry import JarEntry


def compare(
    local_jar_path: str,
    remote_jar_path: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> ComparisonResult:
    """
    로컬 JAR와 운영 JAR를 비교하여 ComparisonResult를 반환한다.

    - missing_in_local: 운영에는 있지만 로컬에 없는 파일
    - modified_files:   양쪽에 모두 있지만 내용이 다른 파일
    - local_only:       로컬에만 있고 운영에 없는 파일
    """

    def _progress(pct: int, msg: str) -> None:
        if progress_callback:
            progress_callback(pct, msg)

    _progress(5, "로컬 JAR 파일 목록 추출 중...")
    local_entries = extract_entries(local_jar_path)

    _progress(20, "운영 JAR 파일 목록 추출 중...")
    remote_entries = extract_entries(remote_jar_path)

    local_keys = set(local_entries.keys())
    remote_keys = set(remote_entries.keys())

    missing_keys = remote_keys - local_keys
    local_only_keys = local_keys - remote_keys
    common_keys = local_keys & remote_keys

    result = ComparisonResult(
        local_jar_path=local_jar_path,
        remote_jar_path=remote_jar_path,
        compared_at=datetime.now(),
        missing_in_local=[remote_entries[k] for k in sorted(missing_keys)],
        local_only=[local_entries[k] for k in sorted(local_only_keys)],
    )

    total = len(common_keys)
    _progress(40, f"공통 파일 {total}개 내용 비교 중...")

    modified = []
    identical = 0

    for idx, key in enumerate(sorted(common_keys)):
        remote_e = remote_entries[key]
        local_e = local_entries[key]

        if remote_e.crc != local_e.crc:
            # CRC 불일치 시 MD5로 2차 검증
            remote_md5 = compute_md5(remote_jar_path, key)
            local_md5 = compute_md5(local_jar_path, key)
            if remote_md5 != local_md5:
                remote_e.hash_md5 = remote_md5
                local_e.hash_md5 = local_md5
                modified.append((remote_e, local_e))
            else:
                identical += 1
        else:
            identical += 1

        if idx % 100 == 0 and total > 0:
            pct = 40 + int((idx / total) * 55)
            _progress(pct, f"공통 파일 비교 중... ({idx}/{total})")

    result.modified_files = modified
    result.identical_count = identical

    _progress(100, "비교 완료")
    return result
