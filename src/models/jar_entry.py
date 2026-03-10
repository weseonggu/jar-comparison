from dataclasses import dataclass, field


@dataclass
class JarEntry:
    path: str
    size: int
    crc: int
    compress_type: int
    hash_md5: str = ""

    def size_str(self) -> str:
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        else:
            return f"{self.size / (1024 * 1024):.1f} MB"
