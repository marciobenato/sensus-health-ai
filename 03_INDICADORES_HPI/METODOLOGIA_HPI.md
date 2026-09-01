# METODOLOGIA DO HPI-R1 — SENSUS HEALTH AI

## Finalidade

O **Hospital Pressure Index — HPI-R1** é um índice acadêmico e comparativo criado para o MVP da Sprint 2. Ele ordena as 62 regiões de saúde de São Paulo por pressão relativa em cada competência de 2025.

Ele **não é um indicador oficial do Ministério da Saúde**, não possui finalidade clínica e não deve ser usado isoladamente para decisão assistencial.

## Indicador 1 — proxy de pressão de permanência sobre leitos SUS

Fórmula do MVP:

`proxy_pressao_leitos_sus_pct = DIAS_PERM total / (LEITOS_SUS × dias do mês) × 100`

A lógica se inspira na relação pacientes-dia / leitos-dia utilizada em indicadores formais de ocupação. Porém, o Sensus Health AI não dispõe do censo diário de pacientes e de leitos operacionais/bloqueados exigidos para a taxa oficial. Por isso, a variável derivada é denominada **proxy**, nunca “taxa oficial de ocupação”.

## Indicador 2 — demanda mensal por leito SUS

`aih_por_leito_sus = AIH distintas no mês / LEITOS_SUS`

O indicador mede intensidade relativa da produção SIH em relação à capacidade SUS disponível na região.

## Normalização

Para cada competência, os dois indicadores são transformados em **percentis entre as 62 regiões de saúde do próprio mês**. Isso evita misturar escala física (%) com razão AIH/leito e reduz interferência da sazonalidade estadual na comparação entre regiões.

## Fórmula HPI-R1

`HPI-R1 = 0,50 × score_pressao_relativo + 0,50 × score_demanda_relativo`

Os pesos são iguais porque não existe, nas fontes usadas no MVP, calibração clínica ou empírica que justifique privilegiar um componente. O projeto evita criar pesos supostamente “científicos” sem validação.

## Criticidade relativa

A classe é definida pelo percentil do HPI dentro do mês:

- até 25: **BAIXA**;
- >25 e até 50: **MODERADA**;
- >50 e até 75: **ALTA**;
- >75: **CRÍTICA**.

Essas faixas são **quartis relativos**, não limiares clínicos ou regulatórios. “Crítica” significa que a região está no estrato superior de pressão **comparativa** naquele mês.

## Tendência

`delta_hpi_mes` mede a diferença do HPI em relação ao mês anterior da mesma região. A tendência é exibida para interpretação, mas **não entra no HPI-R1**, evitando adicionar um terceiro peso sem calibração.

## Referências conceituais

- Ministério da Saúde — indicadores hospitalares: taxa de ocupação operacional calculada pela relação pacientes-dia / leitos operacionais-dia.
- Organização Mundial da Saúde — Bed Occupancy Rate: occupied bed-days / available bed-days.

A diferença entre essas definições e os dados disponíveis no SIH/CNES é a razão para o uso explícito do termo **proxy de pressão**, e não “taxa de ocupação”.
