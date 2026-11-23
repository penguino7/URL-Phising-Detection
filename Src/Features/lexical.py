from collections import Counter
import math
import re
from urllib.parse import unquote

from Src.Core.config import LEXICAL_FEATURES
from Src.Core.constants import SENSITIVE_KEYWORDS
from Src.Core.url_parser import ParsedURL
from Src.Features.base import BaseFeatureExtractor

_HEX_REGEX = re.compile(r"%[0-9a-fA-F]{2}")
_TOKEN_REGEX = re.compile(r"[a-z0-9]+")


class LexicalFeatureExtractor(BaseFeatureExtractor):
    @property
    def feature_names(self) -> list[str]:
        return LEXICAL_FEATURES

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        if not text:
            return 0.0
        length = len(text)
        counts = Counter(text)
        return round(-sum((c / length) * math.log2(c / length) for c in counts.values()), 4)

    @staticmethod
    def _count_sensitive_words(text: str) -> int:
        if not text:
            return 0
        tokens = _TOKEN_REGEX.findall(text.lower())
        return sum(1 for token in tokens if token in SENSITIVE_KEYWORDS)

    def extract(self, parsed: ParsedURL) -> dict[str, int | float]:
        raw_url = parsed.raw_url
        
        url_len = len(raw_url)
        
        url_lower = raw_url.lower()

        letters_count = sum(1 for c in raw_url if c.isalpha())
        
        digits_count = sum(1 for c in raw_url if c.isdigit())
        
        special_count = url_len - (letters_count + digits_count)
        
        uppercase_count = sum(1 for c in raw_url if c.isupper())

        first_proto_idx = url_lower.find("://")
        tail = url_lower[first_proto_idx + 3:] if first_proto_idx != -1 else url_lower
        tail_decoded = unquote(tail)
        has_misplaced_proto = 1 if ("http://" in tail_decoded or "https://" in tail_decoded) else 0

        path = parsed.path
        segments = [s for s in path.split("/") if s]

        query = parsed.query
        query_params = [p for p in query.split("&") if p]
        query_decoded = unquote(query.lower())
        has_embedded_url = 1 if ("http://" in query_decoded or "https://" in query_decoded or "www." in query_decoded) else 0

        return {
            "url_length": url_len,
            "url_letters_count": letters_count,
            "url_letters_ratio": round(letters_count / url_len, 4) if url_len else 0.0,
            "url_digits_count": digits_count,
            "url_digits_ratio": round(digits_count / url_len, 4) if url_len else 0.0,
            "url_special_chars_count": special_count,
            "url_special_chars_ratio": round(special_count / url_len, 4) if url_len else 0.0,
            "url_uppercase_ratio": round(uppercase_count / url_len, 4) if url_len else 0.0,
            "url_char_entropy": self._calculate_entropy(raw_url),
            "url_num_dots": raw_url.count("."),
            "url_num_hyphens": raw_url.count("-"),
            "url_num_underscores": raw_url.count("_"),
            "url_num_slashes": raw_url.count("/"),
            "url_num_questionmarks": raw_url.count("?"),
            "url_num_equals": raw_url.count("="),
            "url_num_at": raw_url.count("@"),
            "url_num_ampersands": raw_url.count("&"),
            "url_num_percents": raw_url.count("%"),
            "is_https": 1 if parsed.scheme == "https" else 0,
            "has_misplaced_protocol": has_misplaced_proto,
            "has_at_symbol": 1 if "@" in raw_url else 0,
            "path_length": len(path),
            "path_depth": len(segments),
            "path_longest_segment_len": max((len(s) for s in segments), default=0),
            "path_entropy": self._calculate_entropy(path),
            "path_sensitive_words_count": self._count_sensitive_words(path),
            "query_length": len(query),
            "query_num_params": len(query_params),
            "has_embedded_url": has_embedded_url,
            "has_fragment": 1 if bool(parsed.fragment) else 0,
            "count_percent_encoding": len(_HEX_REGEX.findall(raw_url)),
            "has_double_encoding": 1 if "%25" in url_lower else 0,
            "query_sensitive_words_count": self._count_sensitive_words(query),
        }
