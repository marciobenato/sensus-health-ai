# Sensus Health AI — Escopo Fechado do MVP — Sprint 2 v1.1

**Grupo:** DataMove  
**Turma:** 1TSCOA  
**Projeto:** Sensus Health AI  
**Escopo revisado em:** 31/08/2026

> **Nota de as-built (01/09/2026):** este arquivo registra o escopo congelado antes da execução. Na implementação real, o SIH foi obtido diretamente pelo FTP oficial DATASUS (em vez de PySUS); a exigência de JSON via API foi atendida pela API oficial CNES Estabelecimentos para os 637 CNES observados no SIH; e a capacidade histórica de leitos veio do recurso oficial Hospitais e Leitos 2025 em JSON. A arquitetura final está documentada em `06_ARQUITETURA/ARQUITETURA_AS_BUILT_SPRINT2.md`.

## 1. Objetivo

Construir um MVP analítico reproduzível capaz de integrar dados públicos do SUS, medir demanda e estrutura hospitalar por município/região de saúde e produzir um **Hospital Pressure Index (HPI) experimental**, ranking de criticidade e visualização navegável para apoio gerencial.

## 2. Recorte analítico congelado

- **Geografia:** Estado de São Paulo (SP).
- **Período de internações:** competências de janeiro a dezembro de **2025**.
- **Granularidade analítica principal:** região de saúde por mês, com base municipal intermediária.
- **Justificativa:** 2025 é um ano fechado para análise de sazonalidade mensal; SP fornece diversidade municipal/regional suficiente sem expandir o MVP para todo o Brasil.

## 3. Fontes obrigatórias e formatos

A especificação segue os três formatos explicitamente exigidos pelo Challenge.

| Fonte | Origem | Formato no MVP | Uso |
|---|---|---|---|
| SIH/SUS — AIH Reduzida | DATASUS via PySUS | Relacional (SQLite) | Internações, competência, permanência e valor hospitalar |
| CNES — Hospitais e Leitos | API oficial DEMAS/MS | JSON | Estrutura hospitalar e leitos SUS |
| Macrorregião e Região de Saúde por Município | API oficial DEMAS/MS | CSV nativo | Regionalização dos municípios |

**Regra:** os dados reais devem ser preservados na área `01_DADOS/raw`/`staging`. Nenhuma fonte sintética substituirá uma fonte oficial ausente.

## 4. Fluxo mínimo

SIH relacional + CNES JSON + Região de Saúde CSV → validação → padronização → integração municipal → agregação por região/mês → indicadores → HPI → ranking/classificação → dashboard → evidências.

## 5. Variáveis mínimas a validar antes do HPI

### SIH/SUS
- município de movimento (`MUNIC_MOV` ou equivalente);
- ano/mês de competência (`ANO_CMPT`, `MES_CMPT`);
- dias de permanência (`DIAS_PERM`);
- valor total da AIH (`VAL_TOT`);
- CNES, quando disponível, para análises complementares.

### CNES
- município;
- CNES do estabelecimento;
- leitos SUS;
- leitos existentes, se disponibilizados;
- leitos UTI SUS, se disponibilizados;
- competência da fotografia, se disponibilizada pela API.

### Região de Saúde
- código do município;
- município;
- UF;
- código e nome da região de saúde;
- macrorregião, quando disponível.

## 6. Regra metodológica mandatória

`DIAS_PERM` representa permanência registrada no SIH. **Não será denominado taxa de ocupação hospitalar.** O MVP analisará pressão demanda-capacidade e utilizará o termo **proxy/índice de pressão assistencial** quando a métrica não representar ocupação observada diretamente.

A fórmula e os pesos do HPI **não estão definidos nesta versão**. Só serão congelados na Etapa 4 após a validação estatística das fontes reais.

## 7. Componentes obrigatórios do MVP

- Python e Pandas;
- ingestão documentada das três fontes;
- persistência relacional da fonte SIH;
- validação e relatório de qualidade;
- dataset analítico município/mês e região/mês;
- EDA e indicadores de demanda/capacidade;
- HPI experimental documentado;
- ranking/classificação regional;
- dashboard navegável;
- código reproduzível, README, evidências e arquitetura as-built.

## 8. Oracle Select AI

O Select AI é classificado como **evolução prioritária do MVP**, pois o regulamento o apresenta como diferencial e inclui perguntas em linguagem natural nos critérios de avaliação. Ele somente será declarado como implementado se houver ambiente Oracle disponível, conexão funcional, objetos carregados e consultas executadas com evidência. O núcleo analítico não dependerá dele para funcionar.

## 9. Critério de aceite

Cada item precisa cumprir: **código → execução real → resultado → validação → evidência → documentação**. Um componente sem execução verificável permanece pendente/roadmap.

## 10. Arquitetura

O desenho da Sprint 1 continua sendo arquitetura proposta. A Sprint 2 apresentará uma arquitetura **as-built**, contendo somente tecnologias comprovadas, e um roadmap separado para componentes planejados.
