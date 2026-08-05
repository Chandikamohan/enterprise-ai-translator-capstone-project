from pathlib import Path
import pandas as pd
import pdfplumber

from utils.exceptions import FileProcessingError


def read_file(file_path: str, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    try:
        if suffix == ".txt":
            return Path(file_path).read_text(encoding="utf-8")
        if suffix == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        if suffix == ".csv":
            df = pd.read_csv(file_path)
            return df.to_csv(index=False)
        if suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(file_path)
            return df.to_csv(index=False)
        raise FileProcessingError(f"Unsupported file type: {suffix}")
    except Exception as exc:
        raise FileProcessingError(str(exc)) from exc
