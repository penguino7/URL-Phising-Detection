from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

DATA_DIR: Path = BASE_DIR / "Data"
DATA_RAW_DIR: Path = DATA_DIR / "Raw"
DATA_INTERIM_DIR: Path = DATA_DIR / "Interim"
DATA_PROCESSED_DIR: Path = DATA_DIR / "Processed"
DATA_EXTERNAL_DIR: Path = DATA_DIR / "External"

MODELS_DIR: Path = BASE_DIR / "Models"
NOTEBOOKS_DIR: Path = BASE_DIR / "Notebooks"
REPORTS_DIR: Path = BASE_DIR / "Reports"
FIGURES_DIR: Path = REPORTS_DIR / "Figures"

LEXICAL_FEATURES: list[str] = [
    "url_length",
    "url_letters_count",
    "url_letters_ratio",
    "url_digits_count",
    "url_digits_ratio",
    "url_special_chars_count",
    "url_special_chars_ratio",
    "url_uppercase_ratio",
    "url_char_entropy",
    "url_num_dots",
    "url_num_hyphens",
    "url_num_underscores",
    "url_num_slashes",
    "url_num_questionmarks",
    "url_num_equals",
    "url_num_at",
    "url_num_ampersands",
    "url_num_percents",
    "is_https",
    "has_misplaced_protocol",
    "has_at_symbol",
    "path_length",
    "path_depth",
    "path_longest_segment_len",
    "path_entropy",
    "path_sensitive_words_count",
    "query_length",
    "query_num_params",
    "has_embedded_url",
    "has_fragment",
    "count_percent_encoding",
    "has_double_encoding",
    "query_sensitive_words_count",
]



