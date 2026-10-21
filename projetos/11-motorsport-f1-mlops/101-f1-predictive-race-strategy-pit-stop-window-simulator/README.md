> **Estado auditado #101: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

# Project #101 — Estratégia Preditiva de Corrida (F1) & Simulador de Janela de Pit-Stop
## F1 Predictive Race Strategy & Pit-Stop Window Simulator

- **Categoria / Route:** `/projetos/motorsport-f1/101` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator`
- **Benchmark de Referência:** `F1 Skill 01 — Predictive Race Strategy (XGBoost / Random Forest)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Modelagem de degradação de pneus, perda de pit-lane, combustível e tráfego com XGBoost/Random Forest para simular janelas de parada e identificar a estratégia de menor tempo total de corrida.

## 2. Industrial & Motorsport Context (EN-US)
Modeling tyre degradation, pit-stop loss, fuel burn, and traffic using XGBoost/Random Forest to simulate pit windows and identify the lowest predicted total race time strategy.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
