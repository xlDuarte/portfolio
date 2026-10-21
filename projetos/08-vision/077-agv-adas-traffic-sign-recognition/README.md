> **Status de implementação #077: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #077 — Reconhecimento de Sinalização para AGVs e Sistemas ADAS
## AGV & ADAS Traffic Sign Recognition

- **Categoria / Route:** `/projetos/vision/77` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/077-agv-adas-traffic-sign-recognition`
- **Benchmark de Referência:** `77 Traffic Sign Recognition`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Identificação de placas de limite de velocidade, pare e rotas demarcadas para veículos autônomos.

## 2. Industrial & Motorsport Context (EN-US)
Identification of speed limits, stop signs, and floor markings for autonomous AGVs/ADAS.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
