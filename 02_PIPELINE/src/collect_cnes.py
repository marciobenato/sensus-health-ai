from __future__ import annotations

import hashlib
import io
import json
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pandas as pd

from .collect_common import CNES_2025_URL, CNES_API_JSON, CNES_ESTAB_BASE, CNES_SNAPSHOT_JSON, PROJECT_ROOT, RAW_AUX, RAW_CNES, REGIOES_API_URL, REGIOES_CSV, request_get, sha256_file, utc_now
from .collect_sih import distinct_cnes_from_sih

def _fetch_cnes_one(code: str) -> dict[str, Any]:
    url = f'{CNES_ESTAB_BASE}/{int(code)}'
    try:
        r = request_get(url, attempts=4, timeout=45, headers={'Accept': 'application/json'})
        payload = r.json()
        if not isinstance(payload, dict):
            return {'codigo_solicitado': code, 'status': 'invalid_payload', 'url': url}
        return {'codigo_solicitado': code, 'status': 'ok', 'url': url, 'registro': payload}
    except Exception as exc:
        return {'codigo_solicitado': code, 'status': 'error', 'url': url, 'erro': str(exc)}

def collect_cnes_api(*, workers: int=6) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    codes = distinct_cnes_from_sih()
    print(f'[CNES API] Consultando {len(codes)} CNES observados no SIH', flush=True)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_fetch_cnes_one, c): c for c in codes}
        done = 0
        for future in as_completed(futures):
            results.append(future.result())
            done += 1
            if done % 50 == 0 or done == len(codes):
                print(f'[CNES API] {done}/{len(codes)}', flush=True)
    results.sort(key=lambda x: x['codigo_solicitado'])
    ok = [x for x in results if x['status'] == 'ok']
    errors = [x for x in results if x['status'] != 'ok']
    coverage = len(ok) / len(codes)
    records = [x['registro'] for x in ok]
    CNES_API_JSON.write_text(json.dumps(records, ensure_ascii=False), encoding='utf-8')
    detail = RAW_CNES / 'cnes_estabelecimentos_sih_sp_2025_api_resultados.json'
    detail.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    meta = {'fonte': 'DEMAS/MS API Dados Abertos — CNES Estabelecimentos', 'endpoint': f'{CNES_ESTAB_BASE}/{{codigo_cnes}}', 'finalidade': 'identificar/enriquecer os estabelecimentos presentes no SIH; capacidade vem do snapshot oficial 2025', 'formato': 'JSON via API', 'cnes_solicitados': len(codes), 'registros_ok': len(ok), 'erros': len(errors), 'cobertura': round(coverage, 6), 'workers': workers, 'arquivo': str(CNES_API_JSON.relative_to(PROJECT_ROOT)), 'sha256': sha256_file(CNES_API_JSON), 'coletado_em_utc': utc_now()}
    (RAW_CNES / 'metadata_cnes_estabelecimentos_sih_sp_2025_api.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    if coverage < 0.95 or errors:
        raise RuntimeError(f'Cobertura CNES API insuficiente: {coverage:.2%}; erros={len(errors)}')
    return (meta, records)

def _json_records(raw: bytes) -> list[dict[str, Any]]:
    text = raw.decode('utf-8-sig', errors='replace')
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return [x for x in obj if isinstance(x, dict)]
        if isinstance(obj, dict):
            for key in ('dados', 'data', 'items', 'results'):
                if isinstance(obj.get(key), list):
                    return [x for x in obj[key] if isinstance(x, dict)]
    except json.JSONDecodeError:
        pass
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        try:
            x = json.loads(line.strip().rstrip(','))
            if isinstance(x, dict):
                out.append(x)
        except Exception:
            continue
    return out

def collect_cnes_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    r = request_get(CNES_2025_URL, timeout=300)
    zip_bytes = r.content
    zip_hash = hashlib.sha256(zip_bytes).hexdigest()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = [n for n in z.namelist() if n.lower().endswith('.json')]
        if not names:
            raise RuntimeError('ZIP CNES 2025 sem JSON')
        records = _json_records(z.read(names[0]))
    sp = [x for x in records if str(x.get('UF', '')).strip().upper() == 'SP' or str(x.get('CO_IBGE', '')).startswith('35')]
    if not sp:
        raise RuntimeError('Snapshot CNES 2025 sem registros de SP')
    CNES_SNAPSHOT_JSON.write_text(json.dumps(sp, ensure_ascii=False), encoding='utf-8')
    comps = sorted({str(x.get('COMP', '')) for x in sp if str(x.get('COMP', ''))})
    meta = {'fonte': 'Portal de Dados Abertos do SUS — Hospitais e Leitos 2025', 'url': CNES_2025_URL, 'formato': 'JSON oficial compactado em ZIP', 'zip_sha256': zip_hash, 'registros_total_arquivo': len(records), 'registros_sp': len(sp), 'competencias_sp': comps, 'arquivo': str(CNES_SNAPSHOT_JSON.relative_to(PROJECT_ROOT)), 'sha256': sha256_file(CNES_SNAPSHOT_JSON), 'coletado_em_utc': utc_now()}
    (RAW_CNES / 'metadata_hospitais_leitos_sp_2025_snapshot.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return (meta, sp)

def collect_regioes_csv() -> tuple[dict[str, Any], pd.DataFrame]:
    r = request_get(REGIOES_API_URL, params={'sigla_uf': 'SP', 'limit': 860, 'offset': 0}, headers={'Accept': 'text/csv'})
    body = r.content
    if body.lstrip().startswith((b'{', b'[')):
        raise RuntimeError('API de regiões devolveu JSON em vez de CSV')
    REGIOES_CSV.write_bytes(body)
    df = pd.read_csv(REGIOES_CSV, sep=';', dtype=str, encoding='utf-8-sig')
    if len(df) < 600 or 'codigo_municipio' not in df or 'codigo_regiao_saude' not in df:
        raise RuntimeError(f'CSV regional inválido: linhas={len(df)} colunas={list(df.columns)}')
    meta = {'fonte': 'DEMAS/MS API Dados Abertos — Região/Macrorregião de Saúde', 'endpoint': REGIOES_API_URL, 'filtro_uf': 'SP', 'formato': 'CSV', 'registros': len(df), 'municipios': int(df['codigo_municipio'].nunique()), 'regioes_saude': int(df['codigo_regiao_saude'].nunique()), 'macrorregioes': int(df['codigo_macrorregiao_saude'].nunique()), 'arquivo': str(REGIOES_CSV.relative_to(PROJECT_ROOT)), 'sha256': sha256_file(REGIOES_CSV), 'coletado_em_utc': utc_now()}
    (RAW_AUX / 'metadata_regioes_saude_sp.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return (meta, df)
