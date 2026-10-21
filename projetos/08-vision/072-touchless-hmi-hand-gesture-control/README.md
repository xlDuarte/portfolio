> **Status de implementação #072: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #072 — Interface HMI sem Toque por Gestos para Operadores
## Touchless HMI Hand Gesture Control

- **Categoria / Route:** `/projetos/vision/72` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/072-touchless-hmi-hand-gesture-control`
- **Benchmark de Referência:** `72 Hand Gesture Recognition`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Controle de painéis operacionais por visão computacional para operadores usando luvas pesadas.

## 2. Industrial & Motorsport Context (EN-US)
Computer-vision control of shop-floor HMIs for operators wearing heavy protective gloves.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
