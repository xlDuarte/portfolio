> **Estado auditado #106: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

# Project #106 — Pipeline MLOps End-to-End com MLflow, Docker & Deploy FastAPI
## End-to-End MLOps Pipeline with MLflow, Docker & FastAPI

- **Categoria / Route:** `/projetos/motorsport-f1/106` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi`
- **Benchmark de Referência:** `Data Mavericks Adv 04 — End to End ML Pipeline (FastAPI, Docker, MLflow)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Ciclo completo de engenharia de Machine Learning: treinamento, rastreamento de experimentos e registro de modelo no MLflow, containerização Docker e publicação de API REST em FastAPI.

## 2. Industrial & Motorsport Context (EN-US)
Complete ML engineering lifecycle: training, experiment tracking and model registry with MLflow, Docker packaging, and live REST API deployment via FastAPI.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
