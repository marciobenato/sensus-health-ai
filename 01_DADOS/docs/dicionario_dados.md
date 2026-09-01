# DICIONÁRIO DE DADOS — ETAPA 2 | SENSUS HEALTH AI

## SIH/SUS — AIH Reduzida (RD)

| Campo | Uso no MVP | Observação |
|---|---|---|
| `MUNIC_MOV` | chave geográfica de atendimento | código IBGE de 6 dígitos; integra ao CSV de Região de Saúde |
| `ANO_CMPT` / `MES_CMPT` | competência | compõem `AAAAMM` |
| `CNES` | estabelecimento | normalizado para 7 dígitos |
| `N_AIH` | identificador da AIH | repetições não são removidas sem regra de negócio |
| `DIAS_PERM` | permanência | não equivale, isoladamente, a taxa oficial de ocupação |
| `VAL_TOT` | valor total da AIH | campo monetário do SIH |
| `MUNIC_RES` | residência do paciente | disponível para análises complementares |
| `MORTE` | desfecho registrado | uso analítico descritivo, não causal |
| `UTI_MES_TO`, `UTI_INT_TO`, `VAL_UTI` | utilização/valor UTI na AIH | uso exploratório |
| `DT_INTER`, `DT_SAIDA` | datas da internação/saída | validação temporal |

## CNES — Hospitais e Leitos 2025

| Campo | Uso no MVP | Observação |
|---|---|---|
| `COMP` | competência mensal | 202501 a 202512 |
| `CNES` | estabelecimento | chave CNES no snapshot |
| `CO_IBGE` | município | chave para regionalização |
| `LEITOS_EXISTENTES` | capacidade total | descritivo |
| `LEITOS_SUS` | capacidade SUS | componente principal de capacidade do MVP |
| `UTI_TOTAL_EXIST` | UTI total existente | descritivo |
| `UTI_TOTAL_SUS` | UTI SUS | componente de capacidade crítica |
| `NOME_ESTABELECIMENTO`, `DS_TIPO_UNIDADE` | identificação | apoio à interpretação |

## API CNES — Estabelecimentos

| Campo | Uso no MVP | Observação |
|---|---|---|
| `codigo_cnes` | validação/enriquecimento | 637/637 CNES observados no SIH recuperados |
| `nome_fantasia` | identificação | cadastro corrente retornado pela API |
| `codigo_municipio` | validação geográfica | não substitui a competência histórica do snapshot |
| `codigo_tipo_unidade` | classificação da unidade | explica parte das ausências no recorte Hospitais/Leitos |
| `estabelecimento_possui_atendimento_hospitalar` | característica atual | campo de enriquecimento |
| `data_atualizacao` | referência de atualização | evidencia que a API é cadastro corrente |

## CSV — Região de Saúde

| Campo | Uso no MVP |
|---|---|
| `codigo_municipio` | join com `MUNIC_MOV` e `CO_IBGE` |
| `municipio` | nome municipal |
| `codigo_regiao_saude`, `regiao_saude` | agrupamento analítico principal |
| `codigo_macrorregiao_saude`, `macrorregiao_saude` | agrupamento superior |
| `populacao_estimada_ibge_2022` | enriquecimento descritivo; não será tratada como população 2025 |
