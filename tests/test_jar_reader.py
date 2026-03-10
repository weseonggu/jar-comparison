import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.create_fixtures import create_fixtures
from src.core.jar_reader import extract_entries, compute_md5, read_entry_bytes


@pytest.fixture(scope="module", autouse=True)
def fixtures():
    create_fixtures()


FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_entries_local():
    entries = extract_entries(str(FIXTURES / "sample_local.jar"))
    assert "com/example/Foo.class" in entries
    assert "com/example/Bar.class" in entries
    assert "com/example/Local.class" in entries
    assert "META-INF/MANIFEST.MF" in entries


def test_extract_entries_remote():
    entries = extract_entries(str(FIXTURES / "sample_remote.jar"))
    assert "com/example/Remote.class" in entries
    assert "com/example/Local.class" not in entries


def test_jar_entry_fields():
    entries = extract_entries(str(FIXTURES / "sample_local.jar"))
    foo = entries["com/example/Foo.class"]
    assert foo.path == "com/example/Foo.class"
    assert foo.size > 0
    assert isinstance(foo.crc, int)


def test_compute_md5():
    md5 = compute_md5(str(FIXTURES / "sample_local.jar"), "com/example/Foo.class")
    assert len(md5) == 32


def test_read_entry_bytes():
    data = read_entry_bytes(str(FIXTURES / "sample_local.jar"), "com/example/Foo.class")
    assert isinstance(data, bytes)
    assert len(data) > 0
