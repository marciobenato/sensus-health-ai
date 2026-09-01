# Dashboard Sensus Health AI — Sprint 2

Dashboard HTML navegável gerado a partir de `01_DADOS/processed/regiao_mes_hpi_2025.csv`.

## Gerar versão de deploy

A versão de deploy é gerada em runtime com Plotly via CDN. O HTML completo não é mantido no histórico Git; o workflow `full-build` o publica como artefato:

```bash
python 04_DASHBOARD/scripts/gerar_dashboard.py --cdn --output 04_DASHBOARD/deploy/index.html
```

## Validar

```bash
python 04_DASHBOARD/scripts/validar_dashboard.py
```

O validador usa por padrão `04_DASHBOARD/deploy/index.html` e verifica:

- 12 competências de 2025;
- 62 regiões por competência;
- ranking, scatter e tendência Plotly;
- seletor interativo por competência;
- dataset analítico incorporado;
- 744 observações região-mês;

Também é possível validar outro HTML explicitamente:

```bash
python 04_DASHBOARD/scripts/validar_dashboard.py --html caminho/arquivo.html
```

## Funcionalidades

- filtro por competência 2025;
- KPIs mensais;
- ranking HPI-R1;
- dispersão pressão × demanda por leito;
- tendência das cinco regiões com maior HPI médio em 2025;
- tabela completa das 62 regiões.

## Nota metodológica

HPI-R1 e criticidade são relativos/comparativos. `proxy_pressao_leitos_sus_pct` **não é taxa oficial de ocupação hospitalar**.

## Publicação

O HTML de deploy está pronto para hospedagem estática. A URL pública só deve ser registrada como concluída depois de publicada e testada externamente. O GitHub não contém uma URL pública inventada ou presumida.
