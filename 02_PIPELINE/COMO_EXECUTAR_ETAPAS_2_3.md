# COMO EXECUTAR — COLETA E PIPELINE

## Pré-requisitos

- Python 3.11+
- acesso à internet para DATASUS e Ministério da Saúde
- espaço em disco para os microdados SIH de SP/2025

## 1. Ambiente

A partir de `fiap/sensus-health-ai/sprint-2`:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/WSL/macOS
# .venv\\Scripts\\Activate.ps1  # Windows PowerShell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Coleta completa das fontes reais

```bash
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage all
```

O coletor executa, na ordem:

1. SIH/SUS SP/2025 → SQLite relacional;
2. CNES Estabelecimentos → JSON via API para os CNES observados no SIH;
3. CNES Hospitais e Leitos 2025 → JSON histórico de capacidade;
4. Região de Saúde → CSV;
5. validação da Etapa 2 e manifesto de integridade.

Ao final, `01_DADOS/quality/relatorio_validacao_dados.md` deve indicar `APROVADO`.

Coletas isoladas também são possíveis:

```bash
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage sih
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage cnes-api
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage cnes-2025
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage regioes
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage validate
```

## 3. Pipeline analítico

Com a Etapa 2 aprovada:

```bash
python 02_PIPELINE/run_pipeline.py
```

Saídas principais:

```text
01_DADOS/processed/demanda_municipio_mes_2025.csv
01_DADOS/processed/capacidade_municipio_mes_2025.csv
01_DADOS/processed/municipio_mes_2025.csv
01_DADOS/processed/regiao_mes_2025.csv
01_DADOS/processed/metadata_pipeline.json
```

O pipeline valida 62 regiões × 12 competências, unicidade das chaves, ausência de capacidade/região faltante e conservação dos registros SIH e da capacidade mensal.

## 4. Continuidade

Após `relatorio_validacao_pipeline_etapa3.md = APROVADO`:

```bash
python 03_INDICADORES_HPI/calcular_hpi.py
python 04_DASHBOARD/scripts/gerar_dashboard.py --cdn --output 04_DASHBOARD/deploy/index.html
python 04_DASHBOARD/scripts/validar_dashboard.py
```

## GitHub Actions

O workflow `.github/workflows/sensus-sprint2-reprodutibilidade.yml` é **somente manual** (`workflow_dispatch`). O modo `full-build` reproduz coleta → pipeline → HPI → dashboard. Nenhuma coleta é disparada automaticamente por `push`.
