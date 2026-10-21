> **Status de implementação #080: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #080 — Classificação de Microestrutura Metalográfica por Imagem
## Metallurgical Microstructure Classifier

- **Categoria / Route:** `/projetos/vision/80` (`08 / 10`)
- **Diretório GitHub:** `projetos/08-vision/080-metallurgical-microstructure-classifier`
- **Benchmark de Referência:** `80 Food Image Classification`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Fluxo de Engenharia (How It Flows):** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção` (`Images -> Preprocess -> CNN -> Detect`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Classificação de fases metalúrgicas (perlita, martensita, bainita) em imagens de microscopia.

## 2. Industrial & Motorsport Context (EN-US)
Classification of metallurgical phases (pearlite, martensite, bainite) from microscopy images.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
