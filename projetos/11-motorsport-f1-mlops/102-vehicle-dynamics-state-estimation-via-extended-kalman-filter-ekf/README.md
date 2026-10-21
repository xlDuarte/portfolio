> **Estado auditado #102: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

# Project #102 — Estimação de Estado em Dinâmica Veicular com Filtro de Kalman Estendido (EKF)
## Vehicle Dynamics State Estimation via Extended Kalman Filter (EKF)

- **Categoria / Route:** `/projetos/motorsport-f1/102` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/102-vehicle-dynamics-state-estimation-via-extended-kalman-filter-ekf`
- **Benchmark de Referência:** `F1 Skill 02 — State Estimation (Vehicle Dynamics EKF)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Implementação de Filtro de Kalman Estendido (EKF) fusionando ângulo de direção, yaw rate e aceleração lateral para estimar o ângulo de deriva veicular (sideslip angle β) e validar contra referência.

## 2. Industrial & Motorsport Context (EN-US)
Extended Kalman Filter (EKF) implementation fusing steering angle, yaw rate, and lateral acceleration to estimate unmeasured vehicle sideslip angle (β) validated against reference telemetry.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
