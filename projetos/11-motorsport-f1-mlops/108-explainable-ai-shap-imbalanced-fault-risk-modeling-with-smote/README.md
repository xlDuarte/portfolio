> **Estado auditado #108: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

# Project #108 — Explicabilidade de Modelos (SHAP) & Eventos Raros com SMOTE
## Explainable AI (SHAP) & Imbalanced Fault/Risk Modeling with SMOTE

- **Categoria / Route:** `/projetos/motorsport-f1/108` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/108-explainable-ai-shap-imbalanced-fault-risk-modeling-with-smote`
- **Benchmark de Referência:** `Data Mavericks Int 01/02/05 — Explainable AI (SHAP) & Imbalanced SMOTE`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Combinação de oversampling sintético (SMOTE) para falhas/fraudes raras altamente desbalanceadas e valores SHAP para explicar o peso exato de cada variável na decisão do modelo.

## 2. Industrial & Motorsport Context (EN-US)
Combining Synthetic Minority Oversampling (SMOTE) for highly imbalanced rare fault/fraud events with SHAP values to explain individual risk drivers transparently.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
