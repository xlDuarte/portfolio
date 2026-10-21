> **Status de implementação #059: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #059 — Recomendador de Rotas e Modais Logísticos
## Optimal Logistics Route & Carrier Engine

- **Categoria / Route:** `/projetos/recommendation/59` (`06 / 10`)
- **Diretório GitHub:** `projetos/06-recommendation/059-optimal-logistics-route-carrier-engine`
- **Benchmark de Referência:** `59 Travel Destination Recommendation`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Scikit-learn, Streamlit`
- **Fluxo de Engenharia (How It Flows):** `Perfil / Ativo -> Similaridade -> Ranking -> Top-N Ações` (`Asset Data -> Similarity -> Rank -> Top-N`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Seleção da melhor combinação transportadora/rota considerando risco climático e tarifa.

## 2. Industrial & Motorsport Context (EN-US)
Selecting the optimal carrier/route combination given weather risk and freight tariff.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
