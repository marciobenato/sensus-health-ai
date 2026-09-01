#!/usr/bin/env python3
"""Validação estrutural e de cobertura do dashboard da Etapa 5."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HTML = ROOT / "04_DASHBOARD" / "deploy" / "index.html"
DATA = ROOT / "01_DADOS" / "processed" / "regiao_mes_hpi_2025.csv"
OUT_MD = ROOT / "01_DADOS" / "quality" / "relatorio_validacao_dashboard_etapa5.md"
OUT_JSON = ROOT / "01_DADOS" / "quality" / "relatorio_validacao_dashboard_etapa5.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida o dashboard HTML gerado")
    parser.add_argument(
        "--html",
        default=str(DEFAULT_HTML),
        help="Caminho do HTML a validar; padrão: 04_DASHBOARD/deploy/index.html",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    html = Path(args.html).resolve()

    checks: list[dict] = []

    def check(name: str, ok: bool, detail: object) -> None:
        checks.append({"check": name, "ok": bool(ok), "detalhe": detail})

    if not html.exists():
        raise FileNotFoundError(html)
    if not DATA.exists():
        raise FileNotFoundError(DATA)

    text = html.read_text(encoding="utf-8")
    df = pd.read_csv(DATA, dtype={"competencia": "string"})
    comps = sorted(df["competencia"].astype(str).unique())
    counts = df.groupby("competencia").size().to_dict()

    check("HTML gerado e não vazio", html.stat().st_size > 100_000, html.stat().st_size)
    check("12 competências disponíveis", comps == [f"2025{m:02d}" for m in range(1, 13)], comps)
    check("Competência padrão 202512", "select.value='202512'" in text, "202512")
    check("Ranking Plotly presente", 'id="ranking"' in text, "div#ranking")
    check("Scatter Plotly presente", 'id="scatter"' in text, "div#scatter")
    check("Tendência Plotly presente", 'id="trend"' in text, "div#trend")
    check("Atualização interativa por competência", 'id="month"' in text and "Plotly.react" in text, "select#month + Plotly.react")
    check("Dataset incorporado no HTML", "const rows =" in text, "JSON analítico embutido")
    check("Sem dependência externa de stylesheet", "<link rel=" not in text.lower(), "CSS incorporado")
    check("Dataset analítico 744 região-mês", len(df) == 744, len(df))
    check("62 regiões por competência", all(int(v) == 62 for v in counts.values()) and len(counts) == 12, counts)

    status = "APROVADO" if all(x["ok"] for x in checks) else "REPROVADO"
    try:
        artifact = str(html.relative_to(ROOT))
    except ValueError:
        artifact = str(html)

    report = {
        "status": status,
        "artefato": artifact,
        "bytes": html.stat().st_size,
        "sha256": sha256(html),
        "checks": checks,
        "limitacao_verificacao": "O sandbox bloqueia teste headless via file:// e localhost; a validação é estrutural e de cobertura dos dados. Isso não equivale a screenshot de runtime do navegador.",
        "nota_metodologica": "HPI-R1 é índice acadêmico relativo; proxy_pressao_leitos_sus_pct não é taxa oficial de ocupação.",
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# RELATÓRIO DE VALIDAÇÃO — ETAPA 5 / DASHBOARD",
        "",
        f"**Status:** `{status}`",
        "",
        f"- Artefato: `{report['artefato']}`",
        f"- Tamanho: {report['bytes']:,} bytes",
        f"- SHA-256: `{report['sha256']}`",
        "",
        "## Verificações",
        "",
        "| Verificação | Resultado | Detalhe |",
        "|---|---|---|",
    ]
    for item in checks:
        detail = str(item["detalhe"]).replace("|", "/").replace("\n", " ")
        lines.append(f"| {item['check']} | {'OK' if item['ok'] else 'FALHA'} | {detail} |")
    lines += [
        "",
        "## Limitação de verificação automática",
        "",
        report["limitacao_verificacao"],
        "",
        "As evidências visuais estáticas pertencem ao pacote de entrega e não são requisito para a reprodução técnica do dashboard a partir do Git.",
        "",
        "## Observação metodológica",
        "",
        report["nota_metodologica"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[DASHBOARD] Validação: {status}")
    print(f"[DASHBOARD] Artefato: {artifact}")
    print(f"[DASHBOARD] SHA-256: {report['sha256']}")
    return 0 if status == "APROVADO" else 9


if __name__ == "__main__":
    raise SystemExit(main())
