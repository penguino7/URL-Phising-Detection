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


