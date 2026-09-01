#!/usr/bin/env python3
"""Etapa 4 — indicadores e HPI relativo do Sensus Health AI.

O HPI deste MVP é um índice acadêmico/comparativo, não um indicador clínico oficial.
Não converte `DIAS_PERM` em taxa oficial de ocupação. A medida derivada é nomeada
explicitamente como proxy de pressão de permanência sobre leitos SUS.
"""
from __future__ import annotations

import calendar
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "01_DADOS"
INPUT = DATA_DIR / "processed" / "regiao_mes_2025.csv"
OUTPUT = DATA_DIR / "processed" / "regiao_mes_hpi_2025.csv"
SUMMARY = DATA_DIR / "processed" / "regiao_resumo_hpi_2025.csv"
QUALITY_JSON = DATA_DIR / "quality" / "relatorio_validacao_hpi_etapa4.json"
QUALITY_MD = DATA_DIR / "quality" / "relatorio_validacao_hpi_etapa4.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_class(percentile: float) -> str:
    if percentile <= 25:
        return "BAIXA"
    if percentile <= 50:
        return "MODERADA"
    if percentile <= 75:
        return "ALTA"
    return "CRITICA"


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        "competencia", "codigo_regiao_saude", "regiao_saude", "ano", "mes",
        "registros_aih", "aih_distintas", "dias_permanencia_total", "valor_total_aih",
        "obitos_registrados", "leitos_sus", "uti_total_sus",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Base analítica sem colunas necessárias: {missing}")

    out = df.copy()
    out["competencia"] = out["competencia"].astype("string")
    out["dias_mes"] = [calendar.monthrange(int(y), int(m))[1] for y, m in zip(out["ano"], out["mes"])]

    # Proxy de pressão: usa dias de permanência registrados no SIH e leitos SUS do CNES.
    # Não equivale à taxa oficial de ocupação, que requer pacientes-dia de censo diário e leitos operacionais-dia.
    out["proxy_pressao_leitos_sus_pct"] = (
        100.0 * out["dias_permanencia_total"]
        / (out["leitos_sus"] * out["dias_mes"]).replace(0, pd.NA)
    )
    out["aih_por_leito_sus"] = out["aih_distintas"] / out["leitos_sus"].replace(0, pd.NA)
    out["uti_sus_por_100_leitos_sus"] = (
        100.0 * out["uti_total_sus"] / out["leitos_sus"].replace(0, pd.NA)
    )
    out["valor_medio_por_aih_registrada"] = (
        out["valor_total_aih"] / out["registros_aih"].replace(0, pd.NA)
    )
    out["obitos_por_100_registros_aih"] = (
        100.0 * out["obitos_registrados"] / out["registros_aih"].replace(0, pd.NA)
    )

    # Componentes relativos dentro de cada competência (62 regiões comparadas no mesmo mês).
    out["score_pressao_relativo"] = (
        out.groupby("competencia")["proxy_pressao_leitos_sus_pct"]
        .rank(pct=True, method="average") * 100.0
    )
    out["score_demanda_relativo"] = (
        out.groupby("competencia")["aih_por_leito_sus"]
        .rank(pct=True, method="average") * 100.0
    )

    # Sem pesos clínicos/empíricos validados, o MVP usa contribuição igual dos dois eixos.
    out["hpi_score"] = 0.5 * out["score_pressao_relativo"] + 0.5 * out["score_demanda_relativo"]
    out["hpi_score"] = out["hpi_score"].round(2)

    out["hpi_percentil_mes"] = (
        out.groupby("competencia")["hpi_score"].rank(pct=True, method="average") * 100.0
    ).round(2)
    out["criticidade_relativa"] = out["hpi_percentil_mes"].map(relative_class)
    out["rank_hpi_mes"] = (
        out.groupby("competencia")["hpi_score"].rank(method="min", ascending=False).astype("Int64")
    )

    # Tendência é mostrada, mas não entra no HPI v1 para evitar peso adicional não calibrado.
    out = out.sort_values(["codigo_regiao_saude", "competencia"]).reset_index(drop=True)
    out["delta_hpi_mes"] = out.groupby("codigo_regiao_saude")["hpi_score"].diff()
    out["delta_proxy_pressao_pp"] = out.groupby("codigo_regiao_saude")["proxy_pressao_leitos_sus_pct"].diff()
    out = out.sort_values(["competencia", "rank_hpi_mes", "codigo_regiao_saude"]).reset_index(drop=True)
    return out


def validate(df: pd.DataFrame) -> dict:
    checks: list[dict] = []
    def check(name: str, ok: bool, detail: object) -> None:
        checks.append({"check": name, "ok": bool(ok), "detalhe": detail})

    expected_comp = {f"2025{m:02d}" for m in range(1, 13)}
    check("744 observações região-mês", len(df) == 744, len(df))
    check("62 regiões por competência", bool((df.groupby("competencia").size() == 62).all()), df.groupby("competencia").size().to_dict())
    check("12 competências", set(df["competencia"].astype(str)) == expected_comp, sorted(df["competencia"].astype(str).unique()))
    check("HPI entre 0 e 100", bool(df["hpi_score"].between(0, 100).all()), {"min": float(df["hpi_score"].min()), "max": float(df["hpi_score"].max())})
    check("Percentil HPI entre 0 e 100", bool(df["hpi_percentil_mes"].between(0, 100).all()), {"min": float(df["hpi_percentil_mes"].min()), "max": float(df["hpi_percentil_mes"].max())})
    metric_cols = [
        "proxy_pressao_leitos_sus_pct", "aih_por_leito_sus", "uti_sus_por_100_leitos_sus",
        "valor_medio_por_aih_registrada", "obitos_por_100_registros_aih",
        "score_pressao_relativo", "score_demanda_relativo", "hpi_score", "hpi_percentil_mes",
    ]
    nulls = {col: int(df[col].isna().sum()) for col in metric_cols}
    check("Indicadores centrais sem nulos", sum(nulls.values()) == 0, nulls)
    negatives = {col: int((df[col] < 0).sum()) for col in ["proxy_pressao_leitos_sus_pct", "aih_por_leito_sus", "uti_sus_por_100_leitos_sus"]}
    check("Indicadores de pressão/capacidade sem negativos", sum(negatives.values()) == 0, negatives)
    valid_classes = {"BAIXA", "MODERADA", "ALTA", "CRITICA"}
    check("Criticidade relativa válida", set(df["criticidade_relativa"]) <= valid_classes, sorted(df["criticidade_relativa"].unique()))

    return {
        "status": "APROVADO" if all(item["ok"] for item in checks) else "REPROVADO",
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "estatisticas": {
            "proxy_pressao_leitos_sus_pct": df["proxy_pressao_leitos_sus_pct"].describe().round(4).to_dict(),
            "aih_por_leito_sus": df["aih_por_leito_sus"].describe().round(4).to_dict(),
            "hpi_score": df["hpi_score"].describe().round(4).to_dict(),
            "classes": df["criticidade_relativa"].value_counts().to_dict(),
        },
        "metodologia": {
            "componente_1": "percentil mensal do proxy DIAS_PERM / (LEITOS_SUS * dias_do_mes)",
            "componente_2": "percentil mensal de AIH distintas / LEITOS_SUS",
            "pesos": {"pressao_permanencia": 0.5, "demanda_por_leito": 0.5},
            "classificacao": "quartis relativos do percentil mensal do HPI; não são faixas clínicas",
            "versao": "HPI-R1",
        },
    }


def render_report(report: dict) -> str:
    lines = [
        "# RELATÓRIO DE VALIDAÇÃO — ETAPA 4 | HPI-R1",
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
        "## Regra do HPI-R1",
        "",
        "`HPI = 50% × score relativo de pressão de permanência + 50% × score relativo de AIH por leito SUS`.",
        "",
        "Os scores dos componentes são percentis calculados **dentro da mesma competência**, comparando as 62 regiões de saúde de SP naquele mês.",
        "",
        "A classificação `BAIXA/MODERADA/ALTA/CRITICA` é **relativa ao conjunto de regiões no mês** e não representa diagnóstico, recomendação clínica ou limiar oficial do Ministério da Saúde.",
        "",
        "## Restrição de nomenclatura",
        "",
        "`proxy_pressao_leitos_sus_pct` não deve ser chamado de taxa oficial de ocupação. A taxa oficial requer pacientes-dia oriundos de censo diário e leitos operacionais-dia; o MVP dispõe de `DIAS_PERM` do SIH e leitos SUS do CNES, portanto trabalha com uma aproximação analítica explicitamente rotulada como proxy.",
    ]
    return "\n".join(lines) + "\n"


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    yearly = (
        df.groupby(["codigo_regiao_saude", "regiao_saude", "codigo_macrorregiao_saude", "macrorregiao_saude"], dropna=False)
        .agg(
            hpi_medio_2025=("hpi_score", "mean"),
            hpi_max_2025=("hpi_score", "max"),
            proxy_pressao_media_2025=("proxy_pressao_leitos_sus_pct", "mean"),
            aih_por_leito_media_2025=("aih_por_leito_sus", "mean"),
            meses_criticidade_relativa_critica=("criticidade_relativa", lambda s: int((s == "CRITICA").sum())),
        )
        .reset_index()
    )
    yearly["rank_hpi_medio_2025"] = yearly["hpi_medio_2025"].rank(method="min", ascending=False).astype("Int64")
    latest = (
        df[df["competencia"] == "202512"][[
            "codigo_regiao_saude", "hpi_score", "rank_hpi_mes", "criticidade_relativa",
            "proxy_pressao_leitos_sus_pct", "aih_por_leito_sus", "delta_hpi_mes"
        ]]
        .rename(columns={
            "hpi_score": "hpi_202512", "rank_hpi_mes": "rank_hpi_202512",
            "criticidade_relativa": "criticidade_relativa_202512",
            "proxy_pressao_leitos_sus_pct": "proxy_pressao_202512",
            "aih_por_leito_sus": "aih_por_leito_202512", "delta_hpi_mes": "delta_hpi_202512",
        })
    )
    return yearly.merge(latest, on="codigo_regiao_saude", how="left", validate="1:1").sort_values("rank_hpi_medio_2025")


def main() -> int:
    if not INPUT.exists():
        raise FileNotFoundError(f"Etapa 3 ausente: {INPUT}")
    df = pd.read_csv(
        INPUT,
        dtype={"competencia": "string", "codigo_regiao_saude": "string", "codigo_macrorregiao_saude": "string"},
    )
    out = calculate(df)
    report = validate(out)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_JSON.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)
    summary = build_summary(out)
    summary.to_csv(SUMMARY, index=False)

    report["arquivos"] = {
        "regiao_mes_hpi_2025": {"path": str(OUTPUT.relative_to(PROJECT_ROOT)), "sha256": sha256(OUTPUT)},
        "regiao_resumo_hpi_2025": {"path": str(SUMMARY.relative_to(PROJECT_ROOT)), "sha256": sha256(SUMMARY)},
    }
    QUALITY_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    QUALITY_MD.write_text(render_report(report), encoding="utf-8")

    print(f"[HPI] Etapa 4: {report['status']}")
    print(f"[HPI] Saída: {OUTPUT} ({len(out):,} linhas)")
    print("[HPI] Top 5 — competência 202512:")
    top = out[out["competencia"] == "202512"].sort_values(["hpi_score", "proxy_pressao_leitos_sus_pct"], ascending=False).head(5)
    print(top[["regiao_saude", "hpi_score", "criticidade_relativa", "proxy_pressao_leitos_sus_pct", "aih_por_leito_sus"]].to_string(index=False))
    return 0 if report["status"] == "APROVADO" else 8


if __name__ == "__main__":
    raise SystemExit(main())
