# Sensus Health AI — Sprint 2 — Master Checklist

DataMove | FIAP 1TSCOA | Sprint 2

## Ordem de execução e estado real

| Etapa | Estado | Critério de aceite |
|---|---|---|
| 1. Fechar exatamente o escopo do MVP | ✅ CONCLUÍDA | Escopo SP/2025 congelado em `01_ESCOPO_MVP_FECHADO_v1.1.md` |
| 2. Montar/validar dados utilizados | ✅ CONCLUÍDA | Fontes reais + `relatorio_validacao_dados.md` = APROVADO |
| 3. Implementar pipeline mínimo | ✅ CONCLUÍDA | 744 região-mês + conservação SIH/capacidade + relatório APROVADO |
| 4. Implementar indicadores + HPI | ✅ CONCLUÍDA | HPI-R1 calculado para 744 observações + relatório APROVADO |
| 5. Produzir visualização/dashboard funcional | ✅ CONCLUÍDA | HTML navegável reproduzível + validação estrutural APROVADA |
| 6. Gerar evidências | ✅ CONCLUÍDA | Catálogo + evidências visuais/técnicas sem simulação de runtime |
| 7. Consolidar GitHub + README | ✅ CONCLUÍDA | Branch final reconstruída a partir da `main`, README atualizado, workflow manual, código/metadados/relatórios/evidências leves versionados; dados pesados excluídos e outputs completos reproduzíveis via Actions artifacts |
| 8. Refazer arquitetura as-built | ✅ CONCLUÍDA | `06_ARQUITETURA/ARQUITETURA_AS_BUILT_SPRINT2.md` separa implementação real de evolução futura |
| 9. Atualizar Planner | ⬜ NÃO INICIADA | Evidenciar execução real e pendências finais |
| 10. Construir PPT Sprint 2 | ⬜ NÃO INICIADA | PPT/PDF aderente ao regulamento e às evidências reais |
| 11. Escrever roteiro do pitch | ⬜ NÃO INICIADA | Roteiro executivo/técnico coerente com o MVP real |
| 12. Gravar demonstração | ⬜ NÃO INICIADA | Vídeo técnico/hands-on ≤5 min conforme regras |
| 13. Publicar YouTube | ⬜ NÃO INICIADA | URL pública validada |
| 14. Preencher Excel/TXT | ⬜ BLOQUEADA PARCIALMENTE | Excel oficial ainda não disponível no workspace; TXT depende do YouTube |
| 15. Montar e validar ZIP final | ⬜ NÃO INICIADA | Pacote único validado contra checklist oficial |

## Regra operacional

Nenhuma tecnologia, fonte, indicador, resultado ou evidência deve ser apresentada como implementada sem prova técnica verificável. Componentes não concluídos devem ser classificados como **evolução futura**.

## Criticidade atual

A prioridade deixou de ser exploração técnica. Com GitHub e arquitetura as-built fechados, o caminho crítico agora é **publicação e apresentação**: validar URL pública do dashboard → atualizar Planner → gerar PPT/roteiro → publicar vídeo → montar pacote final. Mudanças analíticas no HPI-R1 só devem ocorrer se surgir defeito comprovado; alterações cosméticas ou ampliação de escopo estão congeladas.
