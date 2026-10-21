> **Status de implementação #071: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #071 — Verificação Automática de EPIs no Chão de Fábrica
## Shop-Floor PPE Compliance Detection

- **Categoria / Route:** `/projetos/vision/71` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/071-shop-floor-ppe-compliance-detection`
- **Benchmark de Referência:** `71 Face Mask Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Detecção em tempo real do uso de capacete, óculos de proteção e protetor facial em áreas quentes.

## 2. Industrial & Motorsport Context (EN-US)
Real-time detection of helmet, safety goggles, and face shield compliance in hazard zones.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
