import math
import pandas as pd
from joblib import Parallel, delayed

from Src.Core.config import LEXICAL_FEATURES, HOSTING_FEATURES, N_JOBS
from Src.Core.url_parser import ParsedURL, parse_url
from Src.Features.hosting import HostingFeatureExtractor
from Src.Features.lexical import LexicalFeatureExtractor


def _row_to_parsed(row: pd.Series) -> ParsedURL:
    port_val = row["port"]
    return ParsedURL(
        raw_url=row["url"],
        scheme=row["scheme"] if isinstance(row["scheme"], str) else "",
        netloc=row["netloc"] if isinstance(row["netloc"], str) else "",
        host=row["host"] if isinstance(row["host"], str) else "",
        port=int(port_val) if (isinstance(port_val, float) and not math.isnan(port_val)) else None,
        path=row["path"] if isinstance(row["path"], str) else "",
        query=row["query"] if isinstance(row["query"], str) else "",
        fragment="",
        subdomain=row["subdomain"] if isinstance(row["subdomain"], str) else "",
        domain=row["domain"] if isinstance(row["domain"], str) else "",
        suffix=row["suffix"] if isinstance(row["suffix"], str) else "",
        registered_domain=row["registered_domain"] if isinstance(row["registered_domain"], str) else "",
        main_tld=row["main_tld"] if isinstance(row["main_tld"], str) else "",
        is_private_suffix=bool(row["is_private_suffix"]),
    )


def _extract_row(row: pd.Series, lexical: LexicalFeatureExtractor, hosting: HostingFeatureExtractor) -> dict:
    parsed = _row_to_parsed(row)
    return {**lexical.extract(parsed), **hosting.extract(parsed)}


class FeatureExtractor:
    def __init__(self) -> None:
        self._lexical = LexicalFeatureExtractor()
        self._hosting = HostingFeatureExtractor()

    @property
    def feature_names(self) -> list[str]:
        return LEXICAL_FEATURES + HOSTING_FEATURES

    def extract_one(self, url: str) -> dict[str, int | float]:
        parsed = parse_url(url)
        return {**self._lexical.extract(parsed), **self._hosting.extract(parsed)}

    def extract_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = [row for _, row in df.iterrows()]
        results = Parallel(n_jobs=N_JOBS)(
            delayed(_extract_row)(row, self._lexical, self._hosting)
            for row in rows
        )
        return pd.DataFrame(results, columns=self.feature_names, index=df.index)
