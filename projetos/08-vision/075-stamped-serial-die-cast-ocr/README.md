> **Status de implementação #075: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #075 — Reconhecimento Óptico (OCR) de Gravações em Relevo/Punção
## Stamped Serial & Die-Cast OCR

- **Categoria / Route:** `/projetos/vision/75` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/075-stamped-serial-die-cast-ocr`
- **Benchmark de Referência:** `75 Handwritten Digit Recognition`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Leitura automatizada de códigos de corrida siderúrgica e lotes gravados em superfícies metálicas.

## 2. Industrial & Motorsport Context (EN-US)
Automated reading of steel heat numbers and batch codes stamped on metal surfaces.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
