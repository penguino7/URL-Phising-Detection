from collections import Counter
import math
import re

from Src.Core.config import HOSTING_FEATURES
from Src.Core.constants import (
    IPV4_REGEX,
    RISKY_TLDS,
    SENSITIVE_KEYWORDS,
    SHORTENER_DOMAINS,
    STANDARD_PORTS,
    TARGET_BRANDS,
)
from Src.Core.url_parser import ParsedURL
from Src.Features.base import BaseFeatureExtractor

_TOKEN_REGEX = re.compile(r"[a-z0-9]+")
_DWORD_REGEX = re.compile(r"^\d{8,10}$")
_HEX_IP_REGEX = re.compile(r"^0x[0-9a-f]{1,8}$")
_OCTAL_IP_REGEX = re.compile(r"^0[0-7]{1,11}$")


class HostingFeatureExtractor(BaseFeatureExtractor):
    @property
    def feature_names(self) -> list[str]:
        return HOSTING_FEATURES

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
        host = parsed.host
        subdomain = parsed.subdomain
        domain = parsed.domain
        registered_domain = parsed.registered_domain

        # Nhóm IP & Cổng
        is_ip = 1 if IPV4_REGEX.match(host) else 0
        host_parts = host.split(".")
        is_dword_or_hex_octal = 1 if (
            len(host_parts) == 1 and (
                _DWORD_REGEX.match(host) or
                _HEX_IP_REGEX.match(host) or
                _OCTAL_IP_REGEX.match(host)
            )
        ) else 0
        is_non_std_port = 1 if (parsed.port is not None and parsed.port not in STANDARD_PORTS) else 0

        # Nhóm Domain & Subdomain
        subdomain_labels = [s for s in subdomain.split(".") if s] if subdomain else []

        # Nhóm ngữ nghĩa & mạo danh thương hiệu
        reg_domain_lower = registered_domain.lower()
        brand_spoofed = 0
        for brand in TARGET_BRANDS:
            if brand in subdomain and brand not in reg_domain_lower:
                brand_spoofed = 1
                break

        return {
            "is_ip_host": is_ip,
            "is_hex_octal_dword_ip": is_dword_or_hex_octal,
            "is_non_standard_port": is_non_std_port,
            "domain_length": len(host),
            "domain_dots_count": host.count("."),
            "domain_has_hyphen": 1 if "-" in host else 0,
            "domain_digits_count": sum(1 for c in host if c.isdigit()),
            "domain_entropy": self._calculate_entropy(domain),
            "subdomain_levels": len(subdomain_labels),
            "subdomain_length": len(subdomain),
            "registered_domain_len": len(registered_domain),
            "is_risky_tld": 1 if parsed.main_tld in RISKY_TLDS else 0,
            "is_free_hosting": 1 if parsed.is_private_suffix else 0,
            "has_punycode": 1 if "xn--" in host else 0,
            "is_url_shortener": 1 if registered_domain in SHORTENER_DOMAINS else 0,
            "brand_in_subdomain": brand_spoofed,
            "domain_sensitive_words_count": self._count_sensitive_words(host),
        }
