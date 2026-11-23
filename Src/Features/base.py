from abc import ABC, abstractmethod
from Src.Core.url_parser import ParsedURL


class BaseFeatureExtractor(ABC):
    @abstractmethod
    def extract(self, parsed: ParsedURL) -> dict[str, int | float]:
        pass

    @property
    @abstractmethod
    def feature_names(self) -> list[str]:
        pass
