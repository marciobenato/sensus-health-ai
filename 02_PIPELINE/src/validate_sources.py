from __future__ import annotations

import json
import sqlite3
from typing import Any

import pandas as pd

from .collect_common import CNES_API_JSON, CNES_SNAPSHOT_JSON, DATA_DIR, PROJECT_ROOT, QUALITY, REGIOES_CSV, SIH_SQLITE, SIH_TABLE, sha256_file, utc_now

def _norm_muni(v: Any) -> str | None:
    s = '' if v is None else str(v).strip().split('.')[0]
    digits = ''.join((ch for ch in s if ch.isdigit()))
    if not digits:
        return None
    if len(digits) >= 7:
        digits = digits[:6]
    return digits.zfill(6)

def validate_existing() -> dict[str, Any]:
    missing = [str(p.relative_to(PROJECT_ROOT)) for p in (SIH_SQLITE, CNES_API_JSON, CNES_SNAPSHOT_JSON, REGIOES_CSV) if not p.exists() or p.stat().st_size == 0]
    if missing:
        raise FileNotFoundError(f'Fontes ausentes: {missing}')
    with sqlite3.connect(SIH_SQLITE) as conn:
        sih_rows = int(conn.execute(f'SELECT COUNT(*) FROM {SIH_TABLE}').fetchone()[0])
        comps = [f'{int(a):04d}{int(m):02d}' for a, m in conn.execute(f'SELECT DISTINCT ANO_CMPT, MES_CMPT FROM {SIH_TABLE} ORDER BY 1,2').fetchall()]
        sih_munis = {_norm_muni(x[0]) for x in conn.execute(f'SELECT DISTINCT MUNIC_MOV FROM {SIH_TABLE}').fetchall()}
        sih_cnes = {str(x[0]).strip().zfill(7) for x in conn.execute(f"SELECT DISTINCT CNES FROM {SIH_TABLE} WHERE CNES IS NOT NULL AND TRIM(CNES)<>''").fetchall()}
    api = json.loads(CNES_API_JSON.read_text(encoding='utf-8'))
    snapshot = json.loads(CNES_SNAPSHOT_JSON.read_text(encoding='utf-8'))
    reg = pd.read_csv(REGIOES_CSV, sep=';', dtype=str, encoding='utf-8-sig')
    reg_munis = {_norm_muni(x) for x in reg['codigo_municipio']}
    api_codes = {str(x.get('codigo_cnes', '')).strip().split('.')[0].zfill(7) for x in api}
    snapshot_munis = {_norm_muni(x.get('CO_IBGE')) for x in snapshot}
    snapshot_comps = sorted({str(x.get('COMP', '')) for x in snapshot})
    checks = [('SIH: 12 competências', comps == [f'2025{m:02d}' for m in range(1, 13)], comps), ('SIH: registros > 0', sih_rows > 0, sih_rows), ('CNES API: cobertura dos CNES SIH >=95%', len(sih_cnes & api_codes) / max(len(sih_cnes), 1) >= 0.95, f'{len(sih_cnes & api_codes)}/{len(sih_cnes)}'), ('CNES snapshot: 12 competências de 2025', snapshot_comps == [f'2025{m:02d}' for m in range(1, 13)], snapshot_comps), ('CNES snapshot: registros SP >0', len(snapshot) > 0, len(snapshot)), ('Regiões: municípios >=600', int(reg['codigo_municipio'].nunique()) >= 600, int(reg['codigo_municipio'].nunique())), ('Regiões: 62 regiões', int(reg['codigo_regiao_saude'].nunique()) == 62, int(reg['codigo_regiao_saude'].nunique())), ('Cobertura SIH município -> região >=95%', len({x for x in sih_munis if x} & reg_munis) / max(len({x for x in sih_munis if x}), 1) >= 0.95, f'{len({x for x in sih_munis if x} & reg_munis)}/{len({x for x in sih_munis if x})}'), ('Cobertura CNES capacidade município -> região >=95%', len({x for x in snapshot_munis if x} & reg_munis) / max(len({x for x in snapshot_munis if x}), 1) >= 0.95, f'{len({x for x in snapshot_munis if x} & reg_munis)}/{len({x for x in snapshot_munis if x})}')]
    status = 'APROVADO' if all((ok for _, ok, _ in checks)) else 'REPROVADO'
    report = {'status': status, 'uf': 'SP', 'ano': 2025, 'executado_em_utc': utc_now(), 'fontes': {'sih': {'registros': sih_rows, 'competencias': comps, 'cnes_distintos': len(sih_cnes)}, 'cnes_api': {'registros': len(api), 'cobertura_sih': round(len(sih_cnes & api_codes) / max(len(sih_cnes), 1), 6)}, 'cnes_snapshot': {'registros': len(snapshot), 'competencias': snapshot_comps}, 'regioes': {'municipios': int(reg['codigo_municipio'].nunique()), 'regioes': int(reg['codigo_regiao_saude'].nunique()), 'macrorregioes': int(reg['codigo_macrorregiao_saude'].nunique())}}, 'checks': [{'check': n, 'ok': ok, 'detalhe': d} for n, ok, d in checks], 'nota_endpoint_agregado': '/assistencia-a-saude/hospitais-e-leitos retornou HTTP 500 e não é tratado como fonte funcional do as-built.'}
    QUALITY.mkdir(parents=True, exist_ok=True)
    (QUALITY / 'relatorio_validacao_dados.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# RELATÓRIO DE VALIDAÇÃO — DADOS DO MVP', '', f'**Status:** `{status}`  ', '**Recorte:** SP / 2025  ', f"**Execução UTC:** {report['executado_em_utc']}", '', '| Verificação | Resultado | Detalhe |', '|---|---|---|']
    for n, ok, d in checks:
        lines.append(f"| {n} | {('OK' if ok else 'FALHA')} | {str(d).replace('|', '/')} |")
    lines += ['', '## Nota de proveniência', '', report['nota_endpoint_agregado'], '', 'Nenhum dado sintético é gerado para substituir fonte ausente.', '']
    (QUALITY / 'relatorio_validacao_dados.md').write_text('\n'.join(lines), encoding='utf-8')
    if status != 'APROVADO':
        raise RuntimeError('Validação reprovada')
    return report

def write_manifest() -> Path:
    files = []
    for p in sorted(DATA_DIR.rglob('*')):
        if p.is_file():
            files.append({'path': str(p.relative_to(PROJECT_ROOT)), 'bytes': p.stat().st_size, 'sha256': sha256_file(p)})
    out = DATA_DIR / 'MANIFEST_ETAPA_2.json'
    out.write_text(json.dumps({'gerado_em_utc': utc_now(), 'arquivos': files}, ensure_ascii=False, indent=2), encoding='utf-8')
    return out
