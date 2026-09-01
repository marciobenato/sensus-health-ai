from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from .io_utils import canonicalize_columns, extract_records


def normalize_municipio_code(series: pd.Series) -> pd.Series:
    """Normaliza código municipal para a chave de 6 dígitos usada com frequência no SIH.

    Se a fonte trouxer 7 dígitos (código IBGE completo), remove apenas o dígito verificador
    final. Valores não numéricos são mantidos como nulos para inspeção explícita.
    """
    s = series.astype("string").str.replace(r"\D", "", regex=True)
    s = s.where(s.str.len().isin([6, 7]))
    s = s.str.slice(0, 6)
    return s


def find_column(columns, aliases: list[str]) -> str | None:
    cols = set(columns)
    for alias in aliases:
        if alias in cols:
            return alias
    return None


def load_sih(sqlite_path: Path, table: str) -> pd.DataFrame:
    with sqlite3.connect(sqlite_path) as conn:
        df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
    return canonicalize_columns(df)


def load_cnes_json(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    records = extract_records(payload) if not isinstance(payload, list) else payload
    return canonicalize_columns(pd.json_normalize(records))


def read_csv_robust(path: Path) -> pd.DataFrame:
    attempts = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin-1"},
        {"sep": ",", "encoding": "latin-1"},
    ]
    last_exc: Exception | None = None
    for kwargs in attempts:
        try:
            df = pd.read_csv(path, **kwargs)
            if df.shape[1] > 1:
                return canonicalize_columns(df)
        except Exception as exc:  # pragma: no cover - diagnóstico de fonte externa
            last_exc = exc
    raise RuntimeError(f"Não foi possível interpretar CSV {path}: {last_exc}")
