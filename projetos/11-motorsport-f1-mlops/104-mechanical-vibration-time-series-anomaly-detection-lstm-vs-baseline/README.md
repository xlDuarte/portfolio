> **Auditoria do lote #101–#110:** Treino efetivo de LSTM autoencoder TensorFlow/Keras sobre séries artificiais; calibração de erro pela validação e baseline RMS. **Tecnologias comprováveis neste projeto:** TensorFlow/Keras, Scikit-learn, NumPy; treinamento sob flag --run. Todos os resultados e testes são sintéticos, sem dados reais F1 ou indústria, sem homologação de produção. As demais tecnologias citadas no benchmark não estão implícitas neste projeto.

## Como executar a implementação atual

```bash
python -m pip install -r requirements/motorsport-core.txt
python -m pip install -r requirements/motorsport-advanced.txt
python projetos/11-motorsport-f1-mlops/104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline/main.py --run
python -m unittest discover -s tests -p test_motorsport_batch.py -v
```

**Evidência técnica:** [pacote de implementação](../../../motorsport_batch/README.md), [código especializado](../../../motorsport_batch/) e [testes avançados](../../../tests/test_motorsport_advanced.py). Sem `--run`, a CLI só verifica os dados; o treinamento verdadeiro exige `--run`.

# Project #104 — Detecção de Anomalias em Vibração Mecânica com Rede LSTM vs. Baseline
## Mechanical Vibration Time-Series Anomaly Detection (LSTM vs. Baseline)

- **Categoria / Route:** `/projetos/motorsport-f1/104` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline`
- **Benchmark de Referência:** `F1 Skill 04 & Data Mavericks Adv 06 — LSTM Time-Series Anomaly Detection`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack de referência originalmente anunciada:** não é evidência de importação/execução nesta implementação.
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
