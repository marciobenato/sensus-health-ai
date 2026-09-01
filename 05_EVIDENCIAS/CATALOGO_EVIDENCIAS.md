# CATÁLOGO DE EVIDÊNCIAS — GITHUB / SPRINT 2

O repositório versiona **evidências auditáveis e reproduzíveis**, priorizando metadados, relatórios e código. Datasets completos, HTML de deploy e imagens de apresentação são produzidos pelo fluxo e ficam nos artefatos/pacote de entrega, evitando duplicação no histórico Git.

## Evidências versionadas

| Evidência | Finalidade |
|---|---|
| `01_DADOS/raw/sih/metadata_sih_sp_2025.json` | Proveniência, competências, volumes e hashes da coleta SIH |
| `01_DADOS/raw/cnes/metadata_cnes_estabelecimentos_sih_sp_2025_api.json` | Cobertura da API CNES: 637/637 estabelecimentos observados no SIH |
| `01_DADOS/raw/cnes/metadata_hospitais_leitos_sp_2025_snapshot.json` | Proveniência do snapshot oficial de capacidade 2025 |
| `01_DADOS/raw/auxiliar/metadata_regioes_saude_sp.json` | Cobertura de municípios, regiões e macrorregiões |
| `01_DADOS/quality/relatorio_validacao_dados.md` | Aprovação da Etapa 2 |
| `01_DADOS/quality/relatorio_validacao_pipeline_etapa3.md` | Aprovação do pipeline e conservação de registros/capacidade |
| `01_DADOS/quality/relatorio_validacao_hpi_etapa4.md` | Aprovação do HPI-R1 e controles metodológicos |
| `01_DADOS/quality/relatorio_validacao_dashboard_etapa5.md` | Aprovação estrutural e de cobertura do dashboard |
| `06_ARQUITETURA/ARQUITETURA_AS_BUILT_SPRINT2.md` | Arquitetura efetivamente implementada |

## Outputs completos

O workflow manual `Sensus Sprint 2 - Reprodutibilidade`, no modo `full-build`, produz e publica como artefatos:

- datasets município-mês e região-mês;
- dataset completo `regiao_mes_hpi_2025.csv`;
- relatórios de qualidade atualizados;
- `04_DASHBOARD/deploy/index.html`.

## Regra de integridade

Nenhum resultado é apresentado como implementado sem vínculo com código, execução, saída e validação. Componentes sem evidência técnica permanecem classificados como evolução futura.
