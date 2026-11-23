from pathlib import Path
import pandas as pd
from Src.Core.config import DATA_INTERIM_DIR

class URLDataLoader:
    def __init__(self, data_dir: Path = DATA_INTERIM_DIR):
        self.data_dir = data_dir

    def load_clean(self, filename: str = "urls_cleaned.csv") -> pd.DataFrame:
        return pd.read_csv(self.data_dir / filename)

    def load_parsed(self, filename: str = "urls_parsed.csv") -> pd.DataFrame:
        return pd.read_csv(self.data_dir / filename)
