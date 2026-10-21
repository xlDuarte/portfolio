> **Status de implementação #076: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #076 — Detecção de Trincas Superficiais, Porosidade e Oxidação
## Surface Crack & Oxidation Detection

- **Categoria / Route:** `/projetos/vision/76` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/076-surface-crack-oxidation-detection`
- **Benchmark de Referência:** `76 Plant Disease Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Segmentação de defeitos metalúrgicos superficiais em cilindros laminadores e blocos.

## 2. Industrial & Motorsport Context (EN-US)
Segmentation of surface metallurgical defects on rolling mill rolls and forged blocks.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
