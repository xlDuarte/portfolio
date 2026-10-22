> **Auditoria do lote #101–#110:** Treino efetivo CNN TensorFlow sobre radiografias geradas; Grad-CAM calculado por GradientTape e IoU com máscaras artificiais. **Tecnologias comprováveis neste projeto:** TensorFlow/Keras, OpenCV, NumPy; Grad-CAM real, nenhuma inspeção NDT validada. Todos os resultados e testes são sintéticos, sem dados reais F1 ou indústria, sem homologação de produção. As demais tecnologias citadas no benchmark não estão implícitas neste projeto.

## Como executar a implementação atual

```bash
python -m pip install -r requirements-motorsport-core.txt
python -m pip install -r requirements-motorsport-advanced.txt
python projetos/11-motorsport-f1-mlops/105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam/main.py --run
python -m unittest discover -s tests -p test_motorsport_batch.py -v
```

**Evidência técnica:** [pacote de implementação](../../../motorsport_batch/README.md), [código especializado](../../../motorsport_batch/) e [testes avançados](../../../tests/test_motorsport_advanced.py). Sem `--run`, a CLI só verifica os dados; o treinamento verdadeiro exige `--run`.

# Project #105 — Inspeção Radiográfica Industrial (Raio-X NDT) com CNN & Grad-CAM
## Industrial X-Ray NDT Defect Detection with CNN & Grad-CAM

- **Categoria / Route:** `/projetos/motorsport-f1/105` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam`
- **Benchmark de Referência:** `Data Mavericks Adv 01 — X-Ray CNN with Grad-CAM & Transfer Learning`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack de referência originalmente anunciada:** não é evidência de importação/execução nesta implementação.
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
