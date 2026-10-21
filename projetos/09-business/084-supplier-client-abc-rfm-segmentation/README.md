> **Status de implementação #084: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #084 — Segmentação ABC/RFM de Fornecedores e Clientes
## Supplier & Client ABC/RFM Segmentation

- **Categoria / Route:** `/projetos/business/84` (`09 / 10`)
- **Diretório GitHub:** `projetos/09-business/084-supplier-client-abc-rfm-segmentation`
- **Benchmark de Referência:** `84 Customer Segmentation`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `SQL, Power BI, DAX, Scikit-learn, SAP`
- **Fluxo de Engenharia (How It Flows):** `Dados SAP/ERP -> Modelagem DAX -> Dashboard BI -> Decisão ROI` (`Business Data -> Segment / Model -> Dashboard -> Decision`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Clusterização estratégica da base de compras (SAP/ARIBA) e carteira de clientes.

## 2. Industrial & Motorsport Context (EN-US)
Strategic clustering of the SAP/ARIBA supplier base and commercial client portfolio.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
