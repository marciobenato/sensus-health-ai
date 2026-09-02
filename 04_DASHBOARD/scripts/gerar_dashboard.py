#!/usr/bin/env python3
"""Gera o dashboard navegável da Etapa 5 a partir do dataset HPI-R1 real.

Uso:
    python 04_DASHBOARD/scripts/gerar_dashboard.py
    python 04_DASHBOARD/scripts/gerar_dashboard.py --cdn

Por padrão o Plotly.js é incorporado no HTML para produzir um artefato autocontido.
Com --cdn, o HTML fica menor e usa o CDN oficial do Plotly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from plotly.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "01_DADOS" / "processed" / "regiao_mes_hpi_2025.csv"
OUTPUT = ROOT / "04_DASHBOARD" / "index.html"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_data() -> pd.DataFrame:
    if not INPUT.exists():
        raise FileNotFoundError(f"Dataset HPI ausente: {INPUT}")
    df = pd.read_csv(INPUT, dtype={"competencia": "string", "codigo_regiao_saude": "string"})
    expected = {f"2025{m:02d}" for m in range(1, 13)}
    got = set(df["competencia"].astype(str))
    if got != expected:
        raise RuntimeError(f"Competências inesperadas: {sorted(got)}")
    if len(df) != 744 or not (df.groupby("competencia").size() == 62).all():
        raise RuntimeError("Dataset deve conter 744 linhas: 62 regiões x 12 competências")
    return df


def build_html(df: pd.DataFrame, *, use_cdn: bool) -> str:
    keep = [
        "competencia", "regiao_saude", "macrorregiao_saude", "registros_aih", "aih_distintas",
        "dias_permanencia_total", "leitos_sus", "uti_total_sus", "proxy_pressao_leitos_sus_pct",
        "aih_por_leito_sus", "hpi_score", "criticidade_relativa", "rank_hpi_mes", "delta_hpi_mes",
    ]
    records = df[keep].where(pd.notnull(df[keep]), None).to_dict(orient="records")
    data_json = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    plotly_script = (
        '<script src="https://cdn.plot.ly/plotly-3.3.0.min.js"></script>'
        if use_cdn
        else f"<script>{get_plotlyjs()}</script>"
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sensus Health AI — HPI-R1</title>
{plotly_script}
<style>
:root {{ --bg:#f5f7fa; --card:#fff; --text:#182230; --muted:#607080; --line:#d9e0e7; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Arial,Helvetica,sans-serif; background:var(--bg); color:var(--text); }}
main {{ max-width:1480px; margin:auto; padding:22px; }}
header {{ display:flex; gap:18px; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; }}
h1 {{ margin:0 0 6px; font-size:28px; }}
.subtitle {{ color:var(--muted); max-width:900px; line-height:1.45; }}
select {{ padding:9px 12px; border:1px solid var(--line); border-radius:8px; background:white; }}
.kpis {{ display:grid; grid-template-columns:repeat(4,minmax(170px,1fr)); gap:12px; margin:18px 0; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; box-shadow:0 2px 6px rgba(0,0,0,.04); }}
.kpi-label {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
.kpi-value {{ font-size:25px; font-weight:700; margin-top:5px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.plot {{ min-height:430px; }}
.full {{ grid-column:1/-1; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ padding:8px 7px; border-bottom:1px solid var(--line); text-align:right; }}
th:first-child,td:first-child {{ text-align:left; }}
th {{ position:sticky; top:0; background:white; }}
.table-wrap {{ max-height:520px; overflow:auto; }}
.note {{ color:var(--muted); font-size:12px; line-height:1.4; margin-top:14px; }}
@media(max-width:900px) {{ .grid,.kpis {{ grid-template-columns:1fr; }} .full {{ grid-column:auto; }} }}
</style>
</head>
<body>
<main>
<header>
<div>
<h1>Sensus Health AI — HPI-R1</h1>
<div class="subtitle">Pressão hospitalar relativa por Região de Saúde de São Paulo. O HPI-R1 é um índice acadêmico comparativo; a proxy de pressão não é taxa oficial de ocupação hospitalar.</div>
</div>
<label>Competência <select id="month"></select></label>
</header>
<section class="kpis">
<div class="card"><div class="kpi-label">AIH distintas</div><div id="kpi-aih" class="kpi-value">—</div></div>
<div class="card"><div class="kpi-label">Leitos SUS</div><div id="kpi-beds" class="kpi-value">—</div></div>
<div class="card"><div class="kpi-label">Regiões críticas</div><div id="kpi-critical" class="kpi-value">—</div></div>
<div class="card"><div class="kpi-label">HPI máximo</div><div id="kpi-hpi" class="kpi-value">—</div></div>
</section>
<section class="grid">
<div class="card"><div id="ranking" class="plot"></div></div>
<div class="card"><div id="scatter" class="plot"></div></div>
<div class="card full"><div id="trend" class="plot"></div></div>
<div class="card full"><h2>62 regiões — competência selecionada</h2><div class="table-wrap"><table><thead><tr><th>Região</th><th>HPI</th><th>Classe</th><th>AIH</th><th>Leitos SUS</th><th>Proxy pressão (%)</th><th>AIH/leito</th></tr></thead><tbody id="table-body"></tbody></table></div></div>
</section>
<div class="note">Metodologia: HPI-R1 = 50% percentil mensal da proxy DIAS_PERM/(LEITOS_SUS × dias do mês) + 50% percentil mensal de AIH distintas/LEITOS_SUS. Faixas BAIXA/MODERADA/ALTA/CRÍTICA são quartis relativos do próprio mês.</div>
</main>
<script>
const rows = {data_json};
const months = [...new Set(rows.map(r => String(r.competencia)))].sort();
const select = document.getElementById('month');
for (const m of months) {{ const o=document.createElement('option'); o.value=m; o.textContent=m.slice(0,4)+'-'+m.slice(4); select.appendChild(o); }}
select.value='202512';
const fmt=n => Number(n||0).toLocaleString('pt-BR');
const f2=n => Number(n||0).toLocaleString('pt-BR',{{minimumFractionDigits:2,maximumFractionDigits:2}});
const fmtMonth=m => String(m).slice(0,4)+'-'+String(m).slice(4);
function render(month) {{
  const d=rows.filter(r=>String(r.competencia)===month).sort((a,b)=>Number(a.rank_hpi_mes)-Number(b.rank_hpi_mes));
  document.getElementById('kpi-aih').textContent=fmt(d.reduce((s,r)=>s+Number(r.aih_distintas||0),0));
  document.getElementById('kpi-beds').textContent=fmt(d.reduce((s,r)=>s+Number(r.leitos_sus||0),0));
  document.getElementById('kpi-critical').textContent=fmt(d.filter(r=>r.criticidade_relativa==='CRITICA').length);
  document.getElementById('kpi-hpi').textContent=f2(Math.max(...d.map(r=>Number(r.hpi_score||0))));
  const top=[...d].slice(0,15).reverse();
  Plotly.react('ranking',[{{type:'bar',orientation:'h',x:top.map(r=>r.hpi_score),y:top.map(r=>r.regiao_saude),customdata:top.map(r=>r.criticidade_relativa),hovertemplate:'%{{y}}<br>HPI=%{{x:.2f}}<br>%{{customdata}}<extra></extra>'}}],{{title:'Top 15 — HPI-R1',margin:{{l:165,r:25,t:55,b:45}},xaxis:{{range:[0,100],title:'HPI-R1'}}}},{{responsive:true,displaylogo:false}});
  Plotly.react('scatter',[{{type:'scatter',mode:'markers',x:d.map(r=>r.aih_por_leito_sus),y:d.map(r=>r.proxy_pressao_leitos_sus_pct),text:d.map(r=>r.regiao_saude),marker:{{size:d.map(r=>8+Number(r.hpi_score||0)/8)}},hovertemplate:'%{{text}}<br>AIH/leito=%{{x:.2f}}<br>Proxy=%{{y:.2f}}%<extra></extra>'}}],{{title:'Demanda × proxy de pressão',xaxis:{{title:'AIH distintas por leito SUS'}},yaxis:{{title:'Proxy de pressão (%)'}},margin:{{l:65,r:20,t:55,b:55}}}},{{responsive:true,displaylogo:false}});
  const avg={{}}; for(const r of rows){{const k=r.regiao_saude;(avg[k]??=[]).push(Number(r.hpi_score||0));}}
  const leaders=Object.entries(avg).map(([k,v])=>[k,v.reduce((a,b)=>a+b,0)/v.length]).sort((a,b)=>b[1]-a[1]).slice(0,5).map(x=>x[0]);
  const traces=leaders.map(name=>{{const s=rows.filter(r=>r.regiao_saude===name).sort((a,b)=>String(a.competencia).localeCompare(String(b.competencia)));return {{type:'scatter',mode:'lines+markers',name,x:s.map(r=>fmtMonth(r.competencia)),y:s.map(r=>r.hpi_score)}}}});
  Plotly.react('trend',traces,{{title:'Tendência 2025 — cinco maiores HPI médios',yaxis:{{title:'HPI-R1',range:[0,100]}},xaxis:{{title:'Competência',type:'category'}},margin:{{l:60,r:20,t:55,b:55}}}},{{responsive:true,displaylogo:false}});
  const tbody=document.getElementById('table-body'); tbody.innerHTML='';
  for(const r of d){{const tr=document.createElement('tr');tr.innerHTML=`<td>${{r.regiao_saude}}</td><td>${{f2(r.hpi_score)}}</td><td>${{r.criticidade_relativa}}</td><td>${{fmt(r.aih_distintas)}}</td><td>${{fmt(r.leitos_sus)}}</td><td>${{f2(r.proxy_pressao_leitos_sus_pct)}}</td><td>${{f2(r.aih_por_leito_sus)}}</td>`;tbody.appendChild(tr);}}
}}
select.addEventListener('change',()=>render(select.value)); render(select.value);
</script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdn", action="store_true", help="usa Plotly via CDN em vez de incorporar plotly.js")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="caminho de saída do HTML")
    args = parser.parse_args()
    df = load_data()
    html = build_html(df, use_cdn=args.cdn)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"[DASHBOARD] Gerado: {output}")
    print(f"[DASHBOARD] Bytes: {output.stat().st_size}")
    print(f"[DASHBOARD] SHA-256: {sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
