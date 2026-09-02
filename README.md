# Sensus Health AI — Sprint 2

**FIAP Data Science | DataMove | Turma 1TSCOA**

MVP acadêmico para análise comparativa de pressão hospitalar nas **62 Regiões de Saúde do Estado de São Paulo**, utilizando dados oficiais de **2025**.

## Resultado implementado

O fluxo as-built utiliza fontes públicas do Ministério da Saúde/DATASUS, consolida a demanda hospitalar em base relacional, relaciona capacidade CNES por competência, calcula o **Hospital Pressure Index — HPI-R1** e gera um dashboard HTML navegável.

## Links de entrega

- Dashboard informado: https://sensus-health-ai-ib6aujfo9-marciobenato-5064.vercel.app
- Dashboard público alternativo: https://marciobenato.github.io/sensus-health-ai/
- Status do dashboard Vercel: implantação registrada, mas protegida por login da equipe; o GitHub Pages serve a versão validada sem autenticação
- GitHub público: https://github.com/marciobenato/sensus-health-ai
- Vídeo pitch YouTube: https://youtu.be/H-Rs0Oov-tY (publicado como público e validado em navegador anônimo em 2026-09-02)

Resultados técnicos validados:

- **2.950.400** registros SIH/SUS em 12 competências;
- **637/637** estabelecimentos CNES observados no SIH identificados pela API oficial;
- **12.265** registros de Hospitais e Leitos de SP no snapshot oficial 2025;
- **645 municípios**, **62 regiões de saúde** e **19 macrorregiões**;
- **744 observações região-mês** no dataset analítico;
- pipeline, HPI-R1 e dashboard com relatórios de validação `APROVADO`.

## Estrutura

```text
00_CONTROLE/          escopo, status e checklist
01_DADOS/             documentação, metadados, dados analíticos e relatórios
02_PIPELINE/          coleta, transformação e validação
03_INDICADORES_HPI/   cálculo e metodologia do HPI-R1
04_DASHBOARD/         gerador, validador e versão de deploy do dashboard
05_EVIDENCIAS/        catálogo e evidências técnicas
06_ARQUITETURA/       arquitetura as-built
```

## Execução reproduzível

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Coleta completa das fontes reais:

```bash
python 02_PIPELINE/scripts/coleta_dados_reais.py --stage all
```

> A coleta integral exige internet e espaço local para os microdados SIH. Os dados pesados de runtime não ficam no Git.

Pipeline analítico:

```bash
python 02_PIPELINE/run_pipeline.py
```

HPI-R1:

```bash
python 03_INDICADORES_HPI/calcular_hpi.py
```

Dashboard autocontido para uso local:

```bash
python 04_DASHBOARD/scripts/gerar_dashboard.py
```

Versão leve para publicação web + validação reproduzível:

```bash
python 04_DASHBOARD/scripts/gerar_dashboard.py --cdn --output 04_DASHBOARD/deploy/index.html
python 04_DASHBOARD/scripts/validar_dashboard.py
```

## Metodologia

O HPI-R1 combina, em pesos iguais, dois percentis mensais calculados entre as 62 regiões:

1. proxy de pressão de permanência sobre leitos SUS;
2. AIH distintas por leito SUS.

`HPI-R1 = 0,50 × score_pressao_relativo + 0,50 × score_demanda_relativo`.

As classes BAIXA/MODERADA/ALTA/CRÍTICA são **quartis relativos do mês**, não limiares clínicos ou regulatórios.

> `DIAS_PERM / (LEITOS_SUS × dias do mês)` é tratado exclusivamente como **proxy analítica de pressão**. Não é taxa oficial de ocupação hospitalar.

## Limites do as-built

Não são apresentados como implementados nesta Sprint: Oracle Select AI, Oracle DB Silver/Gold, Databricks/Spark, Airflow, Redis, Power BI ou Tableau. Esses itens pertencem somente à evolução futura enquanto não houver evidência técnica de execução.

## Dados no Git

A base SQLite (~395 MB), DBCs e JSONs brutos volumosos não são versionados. O repositório mantém código reproduzível, metadados/hashes, resumos de cobertura, relatórios de qualidade e documentação técnica. Os datasets completos e o HTML de deploy são gerados pelo workflow e publicados como artefatos de execução, evitando inflar o histórico Git.

Consulte `06_ARQUITETURA/ARQUITETURA_AS_BUILT_SPRINT2.md` e `05_EVIDENCIAS/CATALOGO_EVIDENCIAS.md` para rastreabilidade.

## Reprodutibilidade

A reprodução técnica pode ser executada localmente pelos comandos desta página. Os dados pesados e outputs completos permanecem fora do Git e devem ser regenerados ou consultados nos artefatos de entrega, evitando inflar o histórico do repositório público.
