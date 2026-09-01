from __future__ import annotations

import ftplib
import json
import sqlite3
from typing import Any

import pandas as pd
try:
    import pyreaddbc
    from dbfread import DBF
except ImportError:
    pyreaddbc = None
    DBF = None

from .collect_common import PROJECT_ROOT, RAW_SIH, SIH_FTP_DIR, SIH_FTP_HOST, SIH_SQLITE, SIH_TABLE, sha256_file, utc_now

def dbc_to_dataframe(dbc_path: Path) -> pd.DataFrame:
    if pyreaddbc is None or DBF is None:
        raise RuntimeError('Dependências SIH ausentes. Instale requirements.txt (pyreaddbc e dbfread).')
    dbf_path = dbc_path.with_suffix('.dbf')
    dbf_path.unlink(missing_ok=True)
    pyreaddbc.dbc2dbf(str(dbc_path), str(dbf_path))
    try:
        table = DBF(str(dbf_path), encoding='iso-8859-1', load=True, char_decode_errors='ignore')
        return pd.DataFrame(iter(table))
    finally:
        dbf_path.unlink(missing_ok=True)

def collect_sih(*, keep_dbc: bool=False) -> dict[str, Any]:
    SIH_SQLITE.unlink(missing_ok=True)
    required = ['MUNIC_MOV', 'ANO_CMPT', 'MES_CMPT', 'DIAS_PERM', 'VAL_TOT']
    optional = ['UF_ZI', 'CNES', 'N_AIH', 'MUNIC_RES', 'MORTE', 'MARCA_UTI', 'UTI_MES_TO', 'UTI_INT_TO', 'VAL_UTI', 'DT_INTER', 'DT_SAIDA']
    monthly: list[dict[str, Any]] = []
    total = 0
    with sqlite3.connect(SIH_SQLITE) as conn:
        for month in range(1, 13):
            name = f'RDSP25{month:02d}.dbc'
            dest = RAW_SIH / name
            last: Exception | None = None
            for attempt in range(1, 4):
                try:
                    print(f'[SIH] FTP {attempt}/3: {name}', flush=True)
                    with ftplib.FTP(SIH_FTP_HOST, timeout=60) as ftp:
                        ftp.login()
                        ftp.cwd(SIH_FTP_DIR)
                        with dest.open('wb') as f:
                            ftp.retrbinary(f'RETR {name}', f.write, blocksize=1024 * 1024)
                    if dest.stat().st_size < 1000:
                        raise RuntimeError('arquivo muito pequeno')
                    break
                except Exception as exc:
                    last = exc
                    dest.unlink(missing_ok=True)
            else:
                raise RuntimeError(f'Falha FTP {name}: {last}')
            source_hash = sha256_file(dest)
            source_bytes = dest.stat().st_size
            df = dbc_to_dataframe(dest)
            df.columns = [str(c).upper().strip() for c in df.columns]
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise RuntimeError(f'{name} sem colunas mínimas: {missing}')
            keep = [c for c in required + optional if c in df.columns]
            selected = df[keep].copy()
            selected['_COMPETENCIA_COLETA'] = f'2025{month:02d}'
            selected.to_sql(SIH_TABLE, conn, if_exists='append', index=False, chunksize=5000)
            rows = len(selected)
            total += rows
            monthly.append({'arquivo': name, 'url': f'ftp://{SIH_FTP_HOST}{SIH_FTP_DIR}/{name}', 'bytes': source_bytes, 'sha256': source_hash, 'registros': rows})
            print(f'[SIH] {name}: {rows:,}', flush=True)
            if not keep_dbc:
                dest.unlink(missing_ok=True)
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_sih_comp ON {SIH_TABLE} (ANO_CMPT, MES_CMPT)')
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_sih_munic ON {SIH_TABLE} (MUNIC_MOV)')
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_sih_cnes ON {SIH_TABLE} (CNES)')
        conn.commit()
    meta = {'fonte': 'DATASUS SIH/SUS — AIH Reduzida RD', 'meio_acesso': 'FTP oficial DATASUS', 'uf': 'SP', 'ano': 2025, 'registros': total, 'meses': monthly, 'sqlite': str(SIH_SQLITE.relative_to(PROJECT_ROOT)), 'sqlite_bytes': SIH_SQLITE.stat().st_size, 'sqlite_sha256': sha256_file(SIH_SQLITE), 'coletado_em_utc': utc_now()}
    (RAW_SIH / 'metadata_sih_sp_2025.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return meta

def distinct_cnes_from_sih() -> list[str]:
    if not SIH_SQLITE.exists():
        raise FileNotFoundError('SQLite SIH ausente; execute a coleta SIH antes da API CNES')
    with sqlite3.connect(SIH_SQLITE) as conn:
        rows = conn.execute(f"SELECT DISTINCT CNES FROM {SIH_TABLE} WHERE CNES IS NOT NULL AND TRIM(CNES) <> ''").fetchall()
    codes = sorted({str(v[0]).strip().zfill(7) for v in rows if str(v[0]).strip()})
    if not codes:
        raise RuntimeError('Nenhum CNES encontrado no SIH')
    return codes
