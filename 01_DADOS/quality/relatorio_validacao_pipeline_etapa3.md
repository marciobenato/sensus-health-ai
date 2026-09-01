# RELATÓRIO DE VALIDAÇÃO — ETAPA 3 | PIPELINE MÍNIMO

**Status:** `APROVADO`  
**Execução UTC:** 2026-09-01T03:27:21.261991+00:00

| Check | Resultado | Detalhe |
|---|---|---|
| Demanda: 12 competências | OK | ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512'] |
| Capacidade: 12 competências | OK | ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512'] |
| Demanda: chave município+competência única | OK | 0 |
| Capacidade: chave município+competência única | OK | 0 |
| Município-mês: sem região ausente | OK | 0 |
| Município-mês: sem capacidade ausente | OK | 0 |
| Município-mês: uma linha por chave | OK | 0 |
| Região-mês: 62 regiões x 12 competências | OK | 744 |
| Região-mês: chave única | OK | 0 |
| Conservação: registros SIH | OK | {'esperado': 2950400, 'obtido': 2950400} |
| Região-mês: métricas sem negativos | OK | {'registros_aih': 0, 'aih_distintas': 0, 'dias_permanencia_total': 0, 'valor_total_aih': 0, 'obitos_registrados': 0, 'leitos_existentes': 0, 'leitos_sus': 0, 'uti_total_exist': 0, 'uti_total_sus': 0} |
| Conservação: capacidade mensal CNES | OK | somas município→região idênticas |

## Escopo técnico

- A demanda SIH é agregada no SQLite por município e competência antes de chegar ao Pandas.
- `registros_aih` e `aih_distintas` são mantidos separadamente; não se presume que toda repetição de `N_AIH` seja duplicata.
- A capacidade CNES usa a competência correspondente do snapshot 2025; nenhuma fotografia única é repetida artificialmente pelos 12 meses.
- A capacidade regional é agregada a partir de todos os municípios com leitos no snapshot, não apenas dos municípios que tiveram registros SIH.
- HPI, criticidade e proxies de pressão não são calculados nesta etapa.
