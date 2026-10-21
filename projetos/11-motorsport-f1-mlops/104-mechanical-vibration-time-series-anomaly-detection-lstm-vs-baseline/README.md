# Project #104 — Detecção de Anomalias em Vibração Mecânica com Rede LSTM vs. Baseline
## Mechanical Vibration Time-Series Anomaly Detection (LSTM vs. Baseline)

- **Categoria / Route:** `/projetos/motorsport-f1/104` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline`
- **Benchmark de Referência:** `F1 Skill 04 & Data Mavericks Adv 06 — LSTM Time-Series Anomaly Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Treinamento de rede LSTM (Autoencoder) comparada a métodos estatísticos sobre séries temporais de vibração mecânica para identificar desvios incipientes em rolamentos e powertrain.

## 2. Industrial & Motorsport Context (EN-US)
Training an LSTM sequence model compared against statistical baselines on mechanical vibration datasets to reliably identify abnormal operating behavior and incipient faults.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
