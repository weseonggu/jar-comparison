import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.create_fixtures import create_fixtures
from src.core.diff_engine import compute_diff


@pytest.fixture(scope="module", autouse=True)
def fixtures():
    create_fixtures()


FIXTURES = Path(__file__).parent / "fixtures"


def test_diff_binary():
    """바이너리 파일(.class)의 Diff는 is_binary=True이어야 한다."""
    dr = compute_diff(
        str(FIXTURES / "sample_remote.jar"),
        str(FIXTURES / "sample_local.jar"),
        "com/example/Bar.class",
    )
    assert dr.is_binary is True
    assert dr.entry_path == "com/example/Bar.class"
    assert dr.remote_hex != ""
    assert dr.local_hex != ""


def test_diff_text():
    """텍스트 파일(MANIFEST.MF)의 Diff는 is_binary=False이어야 한다."""
    dr = compute_diff(
        str(FIXTURES / "sample_remote.jar"),
        str(FIXTURES / "sample_local.jar"),
        "META-INF/MANIFEST.MF",
    )
    assert dr.is_binary is False
    assert isinstance(dr.remote_lines, list)
    assert isinstance(dr.local_lines, list)


def test_diff_hex_force():
    """use_hex=True이면 텍스트 파일도 hex dump로 표시한다."""
    dr = compute_diff(
        str(FIXTURES / "sample_remote.jar"),
        str(FIXTURES / "sample_local.jar"),
        "META-INF/MANIFEST.MF",
        use_hex=True,
    )
    assert dr.is_binary is True
