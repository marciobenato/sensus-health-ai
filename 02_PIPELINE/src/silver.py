from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from .io_utils import canonicalize_columns


def normalize_code(series: pd.Series, width: int) -> pd.Series:
    values = series.astype("string").str.replace(r"\D", "", regex=True)
    return values.str.zfill(width)


def load_regioes(path: Path) -> pd.DataFrame:
    """Carrega o CSV oficial de regiões e preserva as chaves IBGE de 6 dígitos."""
    df = pd.read_csv(path, sep=";", dtype="string")
    df = canonicalize_columns(df)
    required = [
        "codigo_municipio", "municipio", "codigo_regiao_saude", "regiao_saude",
        "codigo_macrorregiao_saude", "macrorregiao_saude",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"CSV de regiões sem colunas obrigatórias: {missing}")

    df["municipio_chave"] = normalize_code(df["codigo_municipio"], 6)
    keep = [
        "municipio_chave", "municipio", "codigo_regiao_saude", "regiao_saude",
        "codigo_macrorregiao_saude", "macrorregiao_saude",
    ]
    if "populacao_estimada_ibge_2022" in df.columns:
        df["populacao_estimada_ibge_2022"] = pd.to_numeric(
            df["populacao_estimada_ibge_2022"], errors="coerce"
        )
        keep.append("populacao_estimada_ibge_2022")

    out = df[keep].drop_duplicates(subset=["municipio_chave"]).copy()
    if out["municipio_chave"].duplicated().any():
        raise ValueError("Chave municipal duplicada no CSV de regiões")
    return out


def aggregate_sih(sqlite_path: Path, table: str) -> pd.DataFrame:
    """Agrega os 2,95 milhões de registros SIH no próprio SQLite.

    Não chama cada linha de 'internação única': mantém separadamente quantidade de
    registros AIH e quantidade de N_AIH distintos, pois foram observadas repetições
    de N_AIH no microdado real.
    """
    query = f"""
    SELECT
        printf('%06d', CAST(MUNIC_MOV AS INTEGER)) AS municipio_chave,
        CAST(ANO_CMPT AS INTEGER) AS ano,
        CAST(MES_CMPT AS INTEGER) AS mes,
        CAST(ANO_CMPT AS TEXT) || printf('%02d', CAST(MES_CMPT AS INTEGER)) AS competencia,
        COUNT(*) AS registros_aih,
        COUNT(DISTINCT CAST(N_AIH AS TEXT)) AS aih_distintas,
        SUM(CAST(DIAS_PERM AS REAL)) AS dias_permanencia_total,
        AVG(CAST(DIAS_PERM AS REAL)) AS dias_permanencia_media_por_registro,
        SUM(CAST(VAL_TOT AS REAL)) AS valor_total_aih,
        SUM(CASE WHEN CAST(MORTE AS INTEGER) <> 0 THEN 1 ELSE 0 END) AS obitos_registrados,
        COUNT(DISTINCT CAST(CNES AS TEXT)) AS estabelecimentos_com_aih
    FROM "{table}"
    GROUP BY MUNIC_MOV, ANO_CMPT, MES_CMPT
    ORDER BY ANO_CMPT, MES_CMPT, MUNIC_MOV
    """
    with sqlite3.connect(sqlite_path) as conn:
        out = pd.read_sql_query(query, conn)
    out["municipio_chave"] = normalize_code(out["municipio_chave"], 6)
    out["competencia"] = out["competencia"].astype("string")
    return out


def load_capacity_snapshot(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("Snapshot CNES 2025 não contém lista de registros")
    df = canonicalize_columns(pd.DataFrame(payload))
    required = [
        "comp", "co_ibge", "cnes", "leitos_existentes", "leitos_sus",
        "uti_total_exist", "uti_total_sus",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Snapshot CNES sem colunas obrigatórias: {missing}")

    df["competencia"] = df["comp"].astype("string").str.replace(r"\D", "", regex=True).str[:6]
    df["municipio_chave"] = normalize_code(df["co_ibge"], 6)
    df["cnes"] = normalize_code(df["cnes"], 7)
    for col in ["leitos_existentes", "leitos_sus", "uti_total_exist", "uti_total_sus"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    out = (
        df.groupby(["municipio_chave", "competencia"], dropna=False)
        .agg(
            estabelecimentos_com_leitos=("cnes", "nunique"),
            leitos_existentes=("leitos_existentes", "sum"),
            leitos_sus=("leitos_sus", "sum"),
            uti_total_exist=("uti_total_exist", "sum"),
            uti_total_sus=("uti_total_sus", "sum"),
        )
        .reset_index()
        .sort_values(["competencia", "municipio_chave"])
    )
    return out
