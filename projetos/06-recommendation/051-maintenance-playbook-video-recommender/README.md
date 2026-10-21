> **Status de implementação #051: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #051 — Recomendador de Playbooks e Vídeos de Manutenção
## Maintenance Playbook Video Recommender

- **Categoria / Route:** `/projetos/recommendation/51` (`06 / 10`)
- **Diretório GitHub:** `projetos/06-recommendation/051-maintenance-playbook-video-recommender`
- **Benchmark de Referência:** `51 Movie Recommendation System`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, NumPy, Scikit-learn, Streamlit`
- **Fluxo de Engenharia (How It Flows):** `Perfil / Ativo -> Similaridade -> Ranking -> Top-N Ações` (`Asset Data -> Similarity -> Rank -> Top-N`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Sugestão imediata do procedimento visual correto com base no código de falha da máquina.

## 2. Industrial & Motorsport Context (EN-US)
Instant recommendation of the right visual SOP based on machine fault codes.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
