#!/usr/bin/env python3
"""Etapa 3 — pipeline mínimo real do Sensus Health AI.

Entrada: fontes reais aprovadas na Etapa 2.
Saída: datasets analíticos por município-mês e região de saúde-mês.
Nenhum HPI ou faixa de criticidade é calculado neste script.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PIPELINE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_DIR))

from src.config import (  # noqa: E402
    CNES_SNAPSHOT_JSON,
    ETAPA2_REPORT,
    EXPECTED_COMPETENCIAS,
    PROCESSED_DIR,
    PROJECT_ROOT,
    QUALITY_DIR,
    REGIOES_CSV,
    SIH_SQLITE,
    SIH_TABLE,
    YEAR,
)
from src.silver import aggregate_sih, load_capacity_snapshot, load_regioes  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_etapa2() -> dict:
    if not ETAPA2_REPORT.exists():
        raise RuntimeError(f"Relatório da Etapa 2 ausente: {ETAPA2_REPORT}")
    report = json.loads(ETAPA2_REPORT.read_text(encoding="utf-8"))
    if report.get("status") != "APROVADO":
        raise RuntimeError(f"Etapa 2 não aprovada: status={report.get('status')}")
    return report


def validate_outputs(
    demanda: pd.DataFrame,
    capacidade: pd.DataFrame,
    municipio_mes: pd.DataFrame,
    regiao_mes: pd.DataFrame,
    etapa2: dict,
) -> dict:
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: object) -> None:
        checks.append({"check": name, "ok": bool(ok), "detalhe": detail})

    expected = set(EXPECTED_COMPETENCIAS)
    check("Demanda: 12 competências", set(demanda["competencia"].astype(str)) == expected, sorted(demanda["competencia"].unique()))
    check("Capacidade: 12 competências", set(capacidade["competencia"].astype(str)) == expected, sorted(capacidade["competencia"].unique()))
    check("Demanda: chave município+competência única", not demanda.duplicated(["municipio_chave", "competencia"]).any(), int(demanda.duplicated(["municipio_chave", "competencia"]).sum()))
    check("Capacidade: chave município+competência única", not capacidade.duplicated(["municipio_chave", "competencia"]).any(), int(capacidade.duplicated(["municipio_chave", "competencia"]).sum()))
    check("Município-mês: sem região ausente", municipio_mes["codigo_regiao_saude"].notna().all(), int(municipio_mes["codigo_regiao_saude"].isna().sum()))
    check("Município-mês: sem capacidade ausente", municipio_mes["leitos_sus"].notna().all(), int(municipio_mes["leitos_sus"].isna().sum()))
    check("Município-mês: uma linha por chave", not municipio_mes.duplicated(["municipio_chave", "competencia"]).any(), int(municipio_mes.duplicated(["municipio_chave", "competencia"]).sum()))
    check("Região-mês: 62 regiões x 12 competências", len(regiao_mes) == 62 * 12, int(len(regiao_mes)))
    check("Região-mês: chave única", not regiao_mes.duplicated(["codigo_regiao_saude", "competencia"]).any(), int(regiao_mes.duplicated(["codigo_regiao_saude", "competencia"]).sum()))

    expected_sih_rows = int(etapa2["fontes"]["sih"]["registros"])
    check("Conservação: registros SIH", int(regiao_mes["registros_aih"].sum()) == expected_sih_rows, {"esperado": expected_sih_rows, "obtido": int(regiao_mes["registros_aih"].sum())})

    nonnegative_cols = [
        "registros_aih", "aih_distintas", "dias_permanencia_total", "valor_total_aih",
        "obitos_registrados", "leitos_existentes", "leitos_sus", "uti_total_exist", "uti_total_sus",
    ]
    negatives = {col: int((pd.to_numeric(regiao_mes[col], errors="coerce") < 0).sum()) for col in nonnegative_cols}
    check("Região-mês: métricas sem negativos", sum(negatives.values()) == 0, negatives)

    # Capacidade agregada deve ser conservada em cada competência.
    cap_source = capacidade.groupby("competencia")[["leitos_existentes", "leitos_sus", "uti_total_exist", "uti_total_sus"]].sum().sort_index()
    cap_region = regiao_mes.groupby("competencia")[["leitos_existentes", "leitos_sus", "uti_total_exist", "uti_total_sus"]].sum().sort_index()
    cap_equal = cap_source.equals(cap_region)
    check("Conservação: capacidade mensal CNES", cap_equal, "somas município→região idênticas" if cap_equal else "divergência detectada")

    status = "APROVADO" if all(item["ok"] for item in checks) else "REPROVADO"
    return {
        "status": status,
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "resumo": {
            "demanda_municipio_mes_linhas": int(len(demanda)),
            "capacidade_municipio_mes_linhas": int(len(capacidade)),
            "municipio_mes_linhas": int(len(municipio_mes)),
            "regiao_mes_linhas": int(len(regiao_mes)),
            "regioes": int(regiao_mes["codigo_regiao_saude"].nunique()),
            "competencias": int(regiao_mes["competencia"].nunique()),
        },
    }


def render_report(report: dict, path: Path) -> None:
    lines = [
        "# RELATÓRIO DE VALIDAÇÃO — ETAPA 3 | PIPELINE MÍNIMO",
        "",
        f"**Status:** `{report['status']}`  ",
        f"**Execução UTC:** {report['executado_em_utc']}",
        "",
        "| Check | Resultado | Detalhe |",
        "|---|---|---|",
    ]
    for item in report["checks"]:
        detail = str(item["detalhe"]).replace("|", "/").replace("\n", " ")
        lines.append(f"| {item['check']} | {'OK' if item['ok'] else 'FALHA'} | {detail} |")
    lines += [
        "",
        "## Escopo técnico",
        "",
        "- A demanda SIH é agregada no SQLite por município e competência antes de chegar ao Pandas.",
        "- `registros_aih` e `aih_distintas` são mantidos separadamente; não se presume que toda repetição de `N_AIH` seja duplicata.",
        "- A capacidade CNES usa a competência correspondente do snapshot 2025; nenhuma fotografia única é repetida artificialmente pelos 12 meses.",
        "- A capacidade regional é agregada a partir de todos os municípios com leitos no snapshot, não apenas dos municípios que tiveram registros SIH.",
        "- HPI, criticidade e proxies de pressão não são calculados nesta etapa.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    etapa2 = require_etapa2()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    regioes = load_regioes(REGIOES_CSV)
    demanda = aggregate_sih(SIH_SQLITE, SIH_TABLE)
    capacidade = load_capacity_snapshot(CNES_SNAPSHOT_JSON)

    # Demanda municipal + região + capacidade da mesma competência.
    municipio_mes = demanda.merge(regioes, on="municipio_chave", how="left", validate="m:1")
    municipio_mes = municipio_mes.merge(
        capacidade, on=["municipio_chave", "competencia"], how="left", validate="1:1"
    )

    # Região: demanda e capacidade são agregadas separadamente para não excluir
    # leitos de municípios sem registro SIH em uma competência.
    demanda_reg = demanda.merge(regioes, on="municipio_chave", how="left", validate="m:1")
    demanda_regiao = (
        demanda_reg.groupby(
            ["competencia", "codigo_regiao_saude", "regiao_saude", "codigo_macrorregiao_saude", "macrorregiao_saude"],
            dropna=False,
        )
        .agg(
            registros_aih=("registros_aih", "sum"),
            aih_distintas=("aih_distintas", "sum"),
            dias_permanencia_total=("dias_permanencia_total", "sum"),
            valor_total_aih=("valor_total_aih", "sum"),
            obitos_registrados=("obitos_registrados", "sum"),
            estabelecimentos_com_aih=("estabelecimentos_com_aih", "sum"),
            municipios_com_aih=("municipio_chave", "nunique"),
        )
        .reset_index()
    )
    demanda_regiao["dias_permanencia_media_por_registro"] = (
        demanda_regiao["dias_permanencia_total"]
        / demanda_regiao["registros_aih"].replace(0, pd.NA)
    )

    capacidade_reg = capacidade.merge(regioes, on="municipio_chave", how="left", validate="m:1")
    capacidade_regiao = (
        capacidade_reg.groupby(
            ["competencia", "codigo_regiao_saude", "regiao_saude", "codigo_macrorregiao_saude", "macrorregiao_saude"],
            dropna=False,
        )
        .agg(
            estabelecimentos_com_leitos=("estabelecimentos_com_leitos", "sum"),
            leitos_existentes=("leitos_existentes", "sum"),
            leitos_sus=("leitos_sus", "sum"),
            uti_total_exist=("uti_total_exist", "sum"),
            uti_total_sus=("uti_total_sus", "sum"),
            municipios_com_capacidade=("municipio_chave", "nunique"),
        )
        .reset_index()
    )

    join_keys = ["competencia", "codigo_regiao_saude", "regiao_saude", "codigo_macrorregiao_saude", "macrorregiao_saude"]
    regiao_mes = demanda_regiao.merge(capacidade_regiao, on=join_keys, how="outer", validate="1:1")
    regiao_mes["ano"] = pd.to_numeric(regiao_mes["competencia"].str[:4], errors="coerce").astype("Int64")
    regiao_mes["mes"] = pd.to_numeric(regiao_mes["competencia"].str[4:6], errors="coerce").astype("Int64")
    regiao_mes = regiao_mes.sort_values(["competencia", "codigo_regiao_saude"]).reset_index(drop=True)

    demanda_path = PROCESSED_DIR / "demanda_municipio_mes_2025.csv"
    capacidade_path = PROCESSED_DIR / "capacidade_municipio_mes_2025.csv"
    municipio_path = PROCESSED_DIR / "municipio_mes_2025.csv"
    regiao_path = PROCESSED_DIR / "regiao_mes_2025.csv"
    demanda.to_csv(demanda_path, index=False)
    capacidade.to_csv(capacidade_path, index=False)
    municipio_mes.to_csv(municipio_path, index=False)
    regiao_mes.to_csv(regiao_path, index=False)

    report = validate_outputs(demanda, capacidade, municipio_mes, regiao_mes, etapa2)
    report["arquivos"] = {
        "demanda_municipio_mes": {"path": str(demanda_path.relative_to(PROJECT_ROOT)), "sha256": sha256(demanda_path)},
        "capacidade_municipio_mes": {"path": str(capacidade_path.relative_to(PROJECT_ROOT)), "sha256": sha256(capacidade_path)},
        "municipio_mes": {"path": str(municipio_path.relative_to(PROJECT_ROOT)), "sha256": sha256(municipio_path)},
        "regiao_mes": {"path": str(regiao_path.relative_to(PROJECT_ROOT)), "sha256": sha256(regiao_path)},
    }
    report_json = QUALITY_DIR / "relatorio_validacao_pipeline_etapa3.json"
    report_md = QUALITY_DIR / "relatorio_validacao_pipeline_etapa3.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    render_report(report, report_md)

    metadata = {
        "status": "CONCLUIDO" if report["status"] == "APROVADO" else "REPROVADO",
        "etapa": 3,
        "ano": YEAR,
        "granularidades": ["municipio-mes", "regiao-de-saude-mes"],
        "hpi": "NÃO CALCULADO NESTA ETAPA",
        "validacao": str(report_json.relative_to(PROJECT_ROOT)),
        "outputs": report["arquivos"],
    }
    (PROCESSED_DIR / "metadata_pipeline.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[PIPELINE] Etapa 3: {report['status']}")
    print(f"[PIPELINE] Município-mês: {len(municipio_mes):,} linhas")
    print(f"[PIPELINE] Região-mês: {len(regiao_mes):,} linhas")
    return 0 if report["status"] == "APROVADO" else 7


if __name__ == "__main__":
    raise SystemExit(main())
