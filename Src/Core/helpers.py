from pathlib import Path

def load_set_from_file(file_path: Path) -> frozenset[str]:
    if not file_path.exists():
        return frozenset()
    with open(file_path, "r", encoding="utf-8") as f:
        return frozenset(
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        )
