> **Status de implementação #073: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #073 — Detecção e Contagem de Peças Forjadas e Estampadas
## Forged & Stamped Part Detection

- **Categoria / Route:** `/projetos/vision/73` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/073-forged-stamped-part-detection`
- **Benchmark de Referência:** `73 Object Detection System`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Localização via bounding-box e verificação dimensional de componentes na esteira.

## 2. Industrial & Motorsport Context (EN-US)
Bounding-box localization and dimensional verification of components on the conveyor.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
