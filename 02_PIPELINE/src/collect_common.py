from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "01_DADOS"
RAW_SIH = DATA_DIR / "raw" / "sih"
RAW_CNES = DATA_DIR / "raw" / "cnes"
RAW_AUX = DATA_DIR / "raw" / "auxiliar"
STAGING = DATA_DIR / "staging"
QUALITY = DATA_DIR / "quality"
for d in (RAW_SIH, RAW_CNES, RAW_AUX, STAGING, QUALITY):
    d.mkdir(parents=True, exist_ok=True)

SIH_SQLITE = STAGING / "sih_sp_2025.sqlite"
SIH_TABLE = "sih_rd_sp_2025"
CNES_API_JSON = RAW_CNES / "cnes_estabelecimentos_sih_sp_2025_api.json"
CNES_SNAPSHOT_JSON = RAW_CNES / "hospitais_leitos_sp_2025_snapshot.json"
REGIOES_CSV = RAW_AUX / "regioes_saude_sp.csv"

SIH_FTP_HOST = "ftp.datasus.gov.br"
SIH_FTP_DIR = "/dissemin/publicos/SIHSUS/200801_/Dados"
CNES_ESTAB_BASE = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
CNES_2025_URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/Leitos_SUS/json/Leitos_json_2025.zip"
REGIOES_API_URL = "https://apidadosabertos.saude.gov.br/macrorregiao-e-regiao-de-saude/municipio"
USER_AGENT = "SensusHealthAI-FIAP-DataMove/1.0"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def request_get(url: str, *, attempts: int=5, timeout: int=120, **kwargs: Any) -> requests.Response:
    last: Exception | None = None
    headers = dict(kwargs.pop('headers', {}))
    headers.setdefault('User-Agent', USER_AGENT)
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            if r.status_code >= 500:
                raise requests.HTTPError(f'HTTP {r.status_code} para {r.url}', response=r)
            r.raise_for_status()
            return r
        except Exception as exc:
            last = exc
            if attempt < attempts:
                time.sleep(min(2 ** (attempt - 1), 16))
    raise RuntimeError(f'Falha GET {url} após {attempts} tentativas: {last}')
