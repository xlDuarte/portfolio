> **Estado auditado #105: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

# Project #105 — Inspeção Radiográfica Industrial (Raio-X NDT) com CNN & Grad-CAM
## Industrial X-Ray NDT Defect Detection with CNN & Grad-CAM

- **Categoria / Route:** `/projetos/motorsport-f1/105` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam`
- **Benchmark de Referência:** `Data Mavericks Adv 01 — X-Ray CNN with Grad-CAM & Transfer Learning`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Classificação de defeitos internos em radiografias (Raio-X) usando Transfer Learning e mapas de ativação Grad-CAM para explicar visualmente a região exata da anomalia.

## 2. Industrial & Motorsport Context (EN-US)
Training a Transfer Learning CNN on radiographic X-ray images and explaining predictions visually using Grad-CAM activation heatmaps for non-destructive testing (NDT).

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
