# RELATÓRIO DE VALIDAÇÃO — DADOS DO MVP

**Status:** `APROVADO`  
**Recorte:** SP / 2025  
**Execução UTC:** 2026-09-01T03:27:13.794077+00:00

| Verificação | Resultado | Detalhe |
|---|---|---|
| SIH: 12 competências | OK | ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512'] |
| SIH: registros > 0 | OK | 2950400 |
| CNES API: cobertura dos CNES SIH >=95% | OK | 637/637 |
| CNES snapshot: 12 competências de 2025 | OK | ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512'] |
| CNES snapshot: registros SP >0 | OK | 12265 |
| Regiões: municípios >=600 | OK | 645 |
| Regiões: 62 regiões | OK | 62 |
| Cobertura SIH município -> região >=95% | OK | 327/327 |
| Cobertura CNES capacidade município -> região >=95% | OK | 352/352 |

## Nota de proveniência

/assistencia-a-saude/hospitais-e-leitos retornou HTTP 500 e não é tratado como fonte funcional do as-built.

Nenhum dado sintético é gerado para substituir fonte ausente.
