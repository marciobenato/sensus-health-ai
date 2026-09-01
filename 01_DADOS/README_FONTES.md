# FONTES DE DADOS — SENSUS HEALTH AI / SPRINT 2

## Escopo congelado

- **UF:** São Paulo (SP)
- **Período:** competências 202501–202512
- **Unidade analítica:** município/mês → região de saúde/mês
- **Regra de integridade:** nenhuma fonte sintética substitui dado oficial ausente.

## Fonte 1 — SIH/SUS | relacional

**Origem:** DATASUS — Sistema de Informações Hospitalares do SUS, AIH Reduzida (RD).  
**Arquivos:** `RDSP2501.dbc` a `RDSP2512.dbc`.  
**Aquisição efetiva:** FTP oficial DATASUS via `ftplib`.  
**Conversão:** `pyreaddbc` (DBC→DBF) + `dbfread`.  
**Persistência:** `01_DADOS/staging/sih_sp_2025.sqlite`, tabela `sih_rd_sp_2025`.  
**Script definitivo:** `02_PIPELINE/scripts/coleta_dados_reais.py`.

Resultado validado: **2.950.400 registros em 12/12 competências**. A base SQLite (~395 MB) não é versionada no Git; sua proveniência e SHA-256 permanecem nos metadados.

Uso analítico: demanda hospitalar, dias de permanência registrados, valores de AIH, óbitos registrados, estabelecimentos e competência.

## Fonte 2 — CNES Estabelecimentos | JSON via API

**Origem:** DEMAS / Ministério da Saúde.  
**Endpoint utilizado:** `/cnes/estabelecimentos/{codigo_cnes}`.  
**Formato:** JSON via API.  
**Universo consultado:** os **637 CNES distintos efetivamente observados no SIH SP/2025**.  
**Resultado:** **637/637 respostas válidas**, sem substituição sintética.  
**Script definitivo:** `02_PIPELINE/scripts/coleta_dados_reais.py`.

Uso no MVP: identificação e enriquecimento dos estabelecimentos presentes no SIH. Esta API **não é usada como fotografia histórica de capacidade**.

### Restrição registrada

O endpoint agregado `/assistencia-a-saude/hospitais-e-leitos` retornou HTTP 500 em tentativas repetidas. O projeto não o apresenta como fonte operacional bem-sucedida.

## Fonte 3 — CNES Hospitais e Leitos 2025 | JSON oficial

**Origem:** Portal de Dados Abertos do SUS.  
**Recurso:** arquivo anual oficial `Leitos_json_2025.zip`.  
**Formato:** JSON compactado em ZIP.  
**Recorte:** registros de São Paulo.  
**Resultado validado:** **12.265 registros de SP**, com 12 competências.

Uso no MVP: capacidade histórica mensal, principalmente `LEITOS_SUS`, `LEITOS_EXISTENTE`, `UTI_TOTAL_SUS` e `UTI_TOTAL_EXIST` quando disponíveis.

## Fonte 4 — Região/Macrorregião de Saúde | CSV

**Origem:** DEMAS / Ministério da Saúde.  
**Endpoint:** `/macrorregiao-e-regiao-de-saude/municipio`.  
**Formato:** CSV nativo.  
**Filtro:** `sigla_uf=SP`.  
**Arquivo gerado em runtime:** `01_DADOS/raw/auxiliar/regioes_saude_sp.csv`; metadados, cobertura e hash ficam registrados no Git.

Resultado validado: **645 municípios, 62 regiões de saúde e 19 macrorregiões**.

Uso no MVP: regionalização dos indicadores município→região de saúde.

## Política de integridade e versionamento

1. Não gerar registros sintéticos para substituir fontes oficiais.
2. Não editar manualmente dados brutos para “corrigir” resultado.
3. Registrar metadados, origem e SHA-256 das coletas.
4. Bloquear o pipeline em caso de falha de cobertura ou campos essenciais.
5. Não denominar `DIAS_PERM` como taxa oficial de ocupação hospitalar.
6. Dados brutos volumosos (`.dbc`, SQLite e JSONs grandes) ficam fora do Git.
7. O Git mantém código reproduzível, metadados/hashes, resumos de cobertura, relatórios e evidências leves; outputs completos são gerados em runtime e podem ser publicados como artefatos do workflow.
