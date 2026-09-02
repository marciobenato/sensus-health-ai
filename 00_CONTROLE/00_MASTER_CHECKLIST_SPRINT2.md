# Sensus Health AI — Sprint 2 — Master Checklist

DataMove | FIAP 1TSCOA | Sprint 2

## Ordem de execução e estado real

| Etapa | Estado | Critério de aceite |
|---|---|---|
| 1. Fechar exatamente o escopo do MVP | ✅ CONCLUÍDA | Escopo SP/2025 congelado em `01_ESCOPO_MVP_FECHADO_v1.1.md` |
| 2. Montar/validar dados utilizados | ✅ CONCLUÍDA | Fontes reais + `relatorio_validacao_dados.md` = APROVADO |
| 3. Implementar pipeline mínimo | ✅ CONCLUÍDA | 744 região-mês + conservação SIH/capacidade + relatório APROVADO |
| 4. Implementar indicadores + HPI | ✅ CONCLUÍDA | HPI-R1 calculado para 744 observações + relatório APROVADO |
| 5. Produzir visualização/dashboard funcional | ✅ CONCLUÍDA / 🟡 DEPLOY PÚBLICO A REGULARIZAR | HTML navegável gerado em `04_DASHBOARD/deploy/index.html`, validação `APROVADO` e screenshot headless local gerado; URL Vercel informada redirecionou para login no teste anônimo de 2026-09-02 |
| 6. Gerar evidências | ✅ CONCLUÍDA | Catálogo + evidências visuais/técnicas sem simulação de runtime |
| 7. Consolidar GitHub + README | 🟡 A REGULARIZAR | Branch pública/export limpo preparado; falta criar/publicar `marciobenato/sensus-health-ai` como repositório público |
| 8. Refazer arquitetura as-built | ✅ CONCLUÍDA | `06_ARQUITETURA/ARQUITETURA_AS_BUILT_SPRINT2.md` separa implementação real de evolução futura |
| 9. Gestão do projeto | ✅ CONCLUÍDA | Execução real e pendências finais refletidas neste controle; referências antigas a Planner não são requisito bloqueante do repositório público |
| 10. Construir PPT/PDF Sprint 2 | ✅ CONCLUÍDA | Artefatos `EC_Sprint_2_1TSCO_EvidenciasConstrucao_SensusHealthAI_DataMove.pptx` e `.pdf` localizados na pasta de entrega |
| 11. Escrever roteiro do pitch | ✅ CONCLUÍDA | Roteiro incorporado à apresentação/vídeo final entregue como artefato audiovisual |
| 12. Gravar demonstração | ✅ CONCLUÍDA | MP4 `SensusHealthAI.mp4` localizado; duração técnica identificada: 00:02:06.921, dentro do limite regulamentar |
| 13. Publicar YouTube | 🟡 A REGULARIZAR | URL pública/não listada ainda não informada no workspace |
| 14. Validar Excel oficial | ✅ GERADA / ⚠️ VALIDAR TEMPLATE | `Informacoes_Finais_Projeto_Integrantes_v1.xlsx` gerado na pasta de entrega com projeto, grupo, turma e integrantes; validar contra eventual template oficial da FIAP se disponível |
| 15. Montar e validar ZIP final | ✅ CONCLUÍDA | ZIP único recomposto com apresentação, vídeo, código-fonte, arquitetura, gestão do projeto, evidências, README de entrega e planilha de integrantes |

## Regra operacional

Nenhuma tecnologia, fonte, indicador, resultado ou evidência deve ser apresentada como implementada sem prova técnica verificável. Componentes não concluídos devem ser classificados como **evolução futura**.

## Criticidade atual

A prioridade deixou de ser exploração técnica. Com arquitetura as-built, PPT/PDF, vídeo MP4, código-fonte, planilha e ZIP fechados, o caminho crítico restante é **regularização externa**: criar/publicar o GitHub público exclusivo → publicar o vídeo no YouTube como não listado → regularizar o dashboard para acesso sem login → inserir/validar os links finais nos materiais oficiais. Mudanças analíticas no HPI-R1 só devem ocorrer se surgir defeito comprovado; alterações cosméticas ou ampliação de escopo estão congeladas.
