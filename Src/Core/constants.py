import re
from Src.Core.config import DATA_EXTERNAL_DIR
from Src.Core.helpers import load_set_from_file

STANDARD_PORTS: frozenset[int] = frozenset({80, 443})

IPV4_REGEX: re.Pattern = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

RISKY_TLDS: frozenset[str] = load_set_from_file(DATA_EXTERNAL_DIR / "risky_tlds.txt")
SHORTENER_DOMAINS: frozenset[str] = load_set_from_file(DATA_EXTERNAL_DIR / "shorteners.txt")
TARGET_BRANDS: frozenset[str] = load_set_from_file(DATA_EXTERNAL_DIR / "target_brands.txt")
SENSITIVE_KEYWORDS: frozenset[str] = load_set_from_file(DATA_EXTERNAL_DIR / "sensitive_keywords.txt")
