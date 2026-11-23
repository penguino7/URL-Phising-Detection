from dataclasses import dataclass
from urllib.parse import urlparse
import tldextract

@dataclass(slots=True, frozen=True)
class ParsedURL:
    raw_url: str
    scheme: str
    netloc: str
    host: str
    port: int | None
    path: str
    query: str
    fragment: str
    subdomain: str
    domain: str
    suffix: str
    registered_domain: str
    main_tld: str
    is_private_suffix: bool

_EXTRACTOR_PUBLIC = tldextract.TLDExtract(
    suffix_list_urls=None,
    include_psl_private_domains=False,
)

_EXTRACTOR_PRIVATE = tldextract.TLDExtract(
    suffix_list_urls=None,
    include_psl_private_domains=True,
)

def parse_url(url: str) -> ParsedURL:
    url_clean = url.strip()
    has_scheme = "://" in url_clean
    url_for_parsing = url_clean if has_scheme else "http://" + url_clean

    parsed = urlparse(url_for_parsing)
    host = parsed.hostname or ""
    actual_scheme = parsed.scheme.lower() if has_scheme else ""

    ext_public = _EXTRACTOR_PUBLIC(host)
    ext_private = _EXTRACTOR_PRIVATE(host)

    suffix = ext_private.suffix.lower()
    main_tld = suffix.split(".")[-1] if suffix else ""
    is_private_suffix = bool(suffix and suffix != ext_public.suffix.lower())

    if hasattr(ext_private, "top_domain_under_public_suffix"):
        reg_domain = ext_private.top_domain_under_public_suffix
    else:
        reg_domain = ext_private.registered_domain
    registered_domain = reg_domain.lower() if reg_domain else host.lower()

    return ParsedURL(
        raw_url=url_clean,
        scheme=actual_scheme,
        netloc=parsed.netloc,
        host=host.lower(),
        port=parsed.port,
        path=parsed.path,
        query=parsed.query,
        fragment=parsed.fragment,
        subdomain=ext_private.subdomain.lower(),
        domain=ext_private.domain.lower(),
        suffix=suffix,
        registered_domain=registered_domain,
        main_tld=main_tld,
        is_private_suffix=is_private_suffix,
    )

