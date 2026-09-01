import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)


def canonical_name(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text


def canonicalize_columns(df):
    return df.rename(columns={col: canonical_name(col) for col in df.columns})


def extract_records(payload: Any) -> list[dict]:
    """Extrai uma lista de registros de respostas JSON sem pressupor chave específica.

    A API do Ministério pode devolver uma lista diretamente ou um objeto com a lista
    sob alguma chave. Se não houver estrutura reconhecível, falha explicitamente.
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return value
    raise ValueError("Resposta JSON não contém uma lista de registros reconhecível.")
