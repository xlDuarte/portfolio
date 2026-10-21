> **Status de implementação #079: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #079 — Rastreamento de Caminhões e Movimentação no Pátio
## Plant Yard Vehicle & Fleet Tracking

- **Categoria / Route:** `/projetos/vision/79` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/079-plant-yard-vehicle-fleet-tracking`
- **Benchmark de Referência:** `79 Vehicle Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Monitoramento automatizado de fila de pesagem, docas de carga e tempo de permanência.

## 2. Industrial & Motorsport Context (EN-US)
Automated monitoring of weighbridge queues, loading docks, and yard dwell time.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
