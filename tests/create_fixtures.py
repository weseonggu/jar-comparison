"""테스트용 JAR(ZIP) 픽스처를 생성하는 스크립트."""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

FIXTURES = Path(__file__).parent / "fixtures"


def create_fixtures() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)

    # sample_local.jar: 로컬 빌드 JAR
    local_entries = {
        "com/example/Foo.class": b"\xca\xfe\xba\xbe\x00\x00\x00\x37LOCAL_FOO",
        "com/example/Bar.class": b"\xca\xfe\xba\xbe\x00\x00\x00\x37LOCAL_BAR_MODIFIED",
        "com/example/Local.class": b"\xca\xfe\xba\xbe\x00\x00\x00\x37LOCAL_ONLY",
        "META-INF/MANIFEST.MF": b"Manifest-Version: 1.0\nMain-Class: com.example.Main\n",
    }

    # sample_remote.jar: 운영 JAR
    remote_entries = {
        "com/example/Foo.class": b"\xca\xfe\xba\xbe\x00\x00\x00\x37LOCAL_FOO",       # 동일
        "com/example/Bar.class": b"\xca\xfe\xba\xbe\x00\x00\x00\x37REMOTE_BAR_ORIG", # 변경됨
        "com/example/Remote.class": b"\xca\xfe\xba\xbe\x00\x00\x00\x37REMOTE_ONLY",  # 운영에만 있음
        "META-INF/MANIFEST.MF": b"Manifest-Version: 1.0\nMain-Class: com.example.Main\n",
    }

    local_path = FIXTURES / "sample_local.jar"
    with zipfile.ZipFile(local_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in local_entries.items():
            zf.writestr(name, data)

    remote_path = FIXTURES / "sample_remote.jar"
    with zipfile.ZipFile(remote_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in remote_entries.items():
            zf.writestr(name, data)

    print(f"픽스처 생성 완료: {FIXTURES}")


if __name__ == "__main__":
    create_fixtures()
