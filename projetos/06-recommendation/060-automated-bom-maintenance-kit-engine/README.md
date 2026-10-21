> **Status de implementação #060: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #060 — Otimizador de Lotes de Compra e Kits de Manutenção
## Automated BOM & Maintenance Kit Engine

- **Categoria / Route:** `/projetos/recommendation/60` (`06 / 10`)
- **Diretório GitHub:** `projetos/06-recommendation/060-automated-bom-maintenance-kit-engine`
- **Benchmark de Referência:** `60 Personalized Shopping Recommendation`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Scikit-learn, Streamlit`
- **Fluxo de Engenharia (How It Flows):** `Perfil / Ativo -> Similaridade -> Ranking -> Top-N Ações` (`Asset Data -> Similarity -> Rank -> Top-N`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Geração automática de listas de materiais (BOM) completas para paradas programadas.

## 2. Industrial & Motorsport Context (EN-US)
Automated generation of complete Bill-of-Materials (BOM) kits for scheduled shutdowns.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
