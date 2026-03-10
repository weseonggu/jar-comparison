import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.create_fixtures import create_fixtures
from src.core.jar_comparator import compare


@pytest.fixture(scope="module", autouse=True)
def fixtures():
    create_fixtures()


FIXTURES = Path(__file__).parent / "fixtures"


def test_compare_basic():
    local_jar = str(FIXTURES / "sample_local.jar")
    remote_jar = str(FIXTURES / "sample_remote.jar")
    result = compare(local_jar, remote_jar)

    assert result.local_jar_path == local_jar
    assert result.remote_jar_path == remote_jar


def test_missing_in_local():
    """운영에만 있는 파일(Remote.class)이 missing_in_local에 포함되어야 한다."""
    result = compare(
        str(FIXTURES / "sample_local.jar"),
        str(FIXTURES / "sample_remote.jar"),
    )
    missing_paths = [e.path for e in result.missing_in_local]
    assert "com/example/Remote.class" in missing_paths


def test_local_only():
    """로컬에만 있는 파일(Local.class)이 local_only에 포함되어야 한다."""
    result = compare(
        str(FIXTURES / "sample_local.jar"),
        str(FIXTURES / "sample_remote.jar"),
    )
    local_only_paths = [e.path for e in result.local_only]
    assert "com/example/Local.class" in local_only_paths


def test_modified_files():
    """Bar.class는 양쪽 내용이 달라 modified_files에 포함되어야 한다."""
    result = compare(
        str(FIXTURES / "sample_local.jar"),
        str(FIXTURES / "sample_remote.jar"),
    )
    modified_paths = [remote_e.path for remote_e, _ in result.modified_files]
    assert "com/example/Bar.class" in modified_paths


def test_identical():
    """Foo.class와 MANIFEST.MF는 동일하므로 identical_count에 포함되어야 한다."""
    result = compare(
        str(FIXTURES / "sample_local.jar"),
        str(FIXTURES / "sample_remote.jar"),
    )
    assert result.identical_count >= 2


def test_progress_callback():
    """progress_callback이 호출되는지 확인한다."""
    calls = []
    compare(
        str(FIXTURES / "sample_local.jar"),
        str(FIXTURES / "sample_remote.jar"),
        progress_callback=lambda pct, msg: calls.append((pct, msg)),
    )
    assert len(calls) > 0
