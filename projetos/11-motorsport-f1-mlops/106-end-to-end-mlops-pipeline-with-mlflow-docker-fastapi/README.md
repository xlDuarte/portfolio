> **Auditoria técnica #106:** MLflow registra dois treinos efetivos, salva modelos e verifica recarga; há FastAPI de inferência e Dockerfile. Registro remoto e deploy público não implementados. **Stack efetiva:** MLflow, Scikit-learn, FastAPI, Docker; API apenas local. Dados fictícios, nenhuma telemetria de F1 ou inspeção industrial autêntica, nenhuma homologação externa.

## Execução comprovável

```bash
python -m pip install -r requirements/motorsport-core.txt
python -m pip install -r requirements/motorsport-advanced.txt
python projetos/11-motorsport-f1-mlops/106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi/main.py --run
```

**Código e testes:** [módulos executáveis](../../../motorsport_batch/README.md) e [suíte CI](../../../tests/test_motorsport_advanced.py). O modo padrão de inspeção de dados não treina os frameworks pesados; use `--run` para execução integral.

# Project #106 — Pipeline MLOps End-to-End com MLflow, Docker & Deploy FastAPI
## End-to-End MLOps Pipeline with MLflow, Docker & FastAPI

- **Categoria / Route:** `/projetos/motorsport-f1/106` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi`
- **Benchmark de Referência:** `Data Mavericks Adv 04 — End to End ML Pipeline (FastAPI, Docker, MLflow)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Tecnologias de benchmark:** referências aspiracionais, não necessariamente implementadas neste caso.
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
