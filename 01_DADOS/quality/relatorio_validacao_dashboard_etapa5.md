# RELATÓRIO DE VALIDAÇÃO — ETAPA 5 / DASHBOARD

**Status:** `APROVADO`

- Artefato: `04_DASHBOARD/deploy/index.html`
- Tamanho: 291,453 bytes
- SHA-256: `eb17d548b66ba88773c082a14721b76107cccf29fbc8ff31d38446a3b316d53d`

## Verificações

| Verificação | Resultado | Detalhe |
|---|---|---|
| HTML gerado e não vazio | OK | 291453 |
| 12 competências disponíveis | OK | ['202501', '202502', '202503', '202504', '202505', '202506', '202507', '202508', '202509', '202510', '202511', '202512'] |
| Competência padrão 202512 | OK | 202512 |
| Ranking Plotly presente | OK | div#ranking |
| Scatter Plotly presente | OK | div#scatter |
| Tendência Plotly presente | OK | div#trend |
| Atualização interativa por competência | OK | select#month + Plotly.react |
| Dataset incorporado no HTML | OK | JSON analítico embutido |
| Sem dependência externa de stylesheet | OK | CSS incorporado |
| Dataset analítico 744 região-mês | OK | 744 |
| 62 regiões por competência | OK | {'202501': 62, '202502': 62, '202503': 62, '202504': 62, '202505': 62, '202506': 62, '202507': 62, '202508': 62, '202509': 62, '202510': 62, '202511': 62, '202512': 62} |

## Limitação de verificação automática

O sandbox bloqueia teste headless via file:// e localhost; a validação é estrutural e de cobertura dos dados. Isso não equivale a screenshot de runtime do navegador.

As evidências visuais estáticas pertencem ao pacote de entrega e não são requisito para a reprodução técnica do dashboard a partir do Git.

## Observação metodológica

HPI-R1 é índice acadêmico relativo; proxy_pressao_leitos_sus_pct não é taxa oficial de ocupação.
