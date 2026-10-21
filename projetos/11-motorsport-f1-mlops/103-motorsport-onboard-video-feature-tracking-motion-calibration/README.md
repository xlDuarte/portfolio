# Project #103 — Visão Computacional Onboard (F1) — Rastreamento em Frenagem e Curvas
## Motorsport Onboard Video Feature Tracking & Motion Calibration

- **Categoria / Route:** `/projetos/motorsport-f1/103` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/103-motorsport-onboard-video-feature-tracking-motion-calibration`
- **Benchmark de Referência:** `F1 Skill 03 — Computer Vision (Motorsport Video Analysis)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Rastreamento de feições visuais (OpenCV Optical Flow) em câmera onboard para analisar movimento aparente do carro em frenagens e curvas, documentando calibração e limitações físicas.

## 2. Industrial & Motorsport Context (EN-US)
OpenCV optical-flow feature tracking on onboard footage to analyze apparent vehicle motion during braking and cornering, documenting calibration constraints and measurement limitations.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
