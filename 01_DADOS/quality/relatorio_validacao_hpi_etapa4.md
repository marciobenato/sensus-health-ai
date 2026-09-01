# RELATÓRIO DE VALIDAÇÃO — ETAPA 4 | HPI-R1

**Status:** `APROVADO`  
**Execução UTC:** 2026-09-01T03:27:22.196680+00:00

| Check | Resultado | Detalhe |
|---|---|---|
| 744 observações região-mês | OK | 744 |
| 62 regiões por competência | OK | {'202501': 62, '202502': 62, '202503': 62, '202504': 62, '202505': 62, '202506': 62, '202507': 62, '202508': 62, '202509': 62, '202510': 62, '202511': 62, '202512': 62} |
| 12 competências | OK | ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512'] |
| HPI entre 0 e 100 | OK | {'min': 1.61, 'max': 100.0} |
| Percentil HPI entre 0 e 100 | OK | {'min': 1.61, 'max': 100.0} |
| Indicadores centrais sem nulos | OK | {'proxy_pressao_leitos_sus_pct': 0, 'aih_por_leito_sus': 0, 'uti_sus_por_100_leitos_sus': 0, 'valor_medio_por_aih_registrada': 0, 'obitos_por_100_registros_aih': 0, 'score_pressao_relativo': 0, 'score_demanda_relativo': 0, 'hpi_score': 0, 'hpi_percentil_mes': 0} |
| Indicadores de pressão/capacidade sem negativos | OK | {'proxy_pressao_leitos_sus_pct': 0, 'aih_por_leito_sus': 0, 'uti_sus_por_100_leitos_sus': 0} |
| Criticidade relativa válida | OK | ['ALTA', 'BAIXA', 'CRITICA', 'MODERADA'] |

## Regra do HPI-R1

`HPI = 50% × score relativo de pressão de permanência + 50% × score relativo de AIH por leito SUS`.

Os scores dos componentes são percentis calculados **dentro da mesma competência**, comparando as 62 regiões de saúde de SP naquele mês.

A classificação `BAIXA/MODERADA/ALTA/CRITICA` é **relativa ao conjunto de regiões no mês** e não representa diagnóstico, recomendação clínica ou limiar oficial do Ministério da Saúde.

## Restrição de nomenclatura

`proxy_pressao_leitos_sus_pct` não deve ser chamado de taxa oficial de ocupação. A taxa oficial requer pacientes-dia oriundos de censo diário e leitos operacionais-dia; o MVP dispõe de `DIAS_PERM` do SIH e leitos SUS do CNES, portanto trabalha com uma aproximação analítica explicitamente rotulada como proxy.
