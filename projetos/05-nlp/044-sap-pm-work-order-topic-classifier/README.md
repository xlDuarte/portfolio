> **Status de implementação #044: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #044 — Classificação Automática de Ordens de Manutenção (SAP PM)
## SAP PM Work-Order Topic Classifier

- **Categoria / Route:** `/projetos/nlp/44` (`05 / 10`)
- **Diretório GitHub:** `projetos/05-nlp/044-sap-pm-work-order-topic-classifier`
- **Benchmark de Referência:** `44 News Topic Classification`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `NLTK, spaCy, Hugging Face, Scikit-learn`
- **Fluxo de Engenharia (How It Flows):** `Texto Técnico -> Tokenização -> Modelo NLP -> Classificação` (`Text -> Tokenize -> Model -> Output`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Categorização de notas de manutenção (elétrica, mecânica, hidráulica, automação) via texto livre.

## 2. Industrial & Motorsport Context (EN-US)
Categorizing free-text maintenance notes into electrical, mechanical, hydraulic, or automation.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
