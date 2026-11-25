> **Atualização científica (fase 3):** estimação do ângulo de deriva com bicicleta não linear e Magic Formula calibrada (fase 1), EKF e UKF em lote com viés do giroscópio no estado, versão aumentada que estima o fator de aderência λ, e estudo de Monte Carlo (40 execuções, volta completa do Bahrein) com verdade simulada mais rica que o modelo dos filtros. Consistência medida por NEES/NIS contra a faixa χ². UKF + λ: erro de β de 0,16° e queda de aderência de 10 % detectada como 8,8 %. Dados simulados: o OpenF1 não publica IMU. Código em [`state_estimation/`](../../../state_estimation/), método em [docs/physics/ESTIMATION.md](../../../docs/physics/ESTIMATION.md).

> **Auditoria do lote #101–#110:** Estimador EKF escalar de sideslip por dinâmica simplificada e sensores artificiais. Não é filtro multiestado calibrado em carro real. **Tecnologias comprováveis neste projeto:** Python, matemática e dados de sensores sintéticos; sem sensores físicos. Todos os resultados e testes são sintéticos, sem dados reais F1 ou indústria, sem homologação de produção. As demais tecnologias citadas no benchmark não estão implícitas neste projeto.

## Como executar a implementação atual

```bash
python -m pip install -r requirements/motorsport-core.txt
python projetos/11-motorsport-f1-mlops/102-vehicle-dynamics-state-estimation-via-extended-kalman-filter-ekf/main.py
python -m unittest discover -s tests -p test_motorsport_batch.py -v
```

**Evidência técnica:** [pacote de implementação](../../../motorsport_batch/README.md), [código especializado](../../../motorsport_batch/) e [testes avançados](../../../tests/test_motorsport_advanced.py). 

# Project #102 — Estimação de Estado em Dinâmica Veicular com Filtro de Kalman Estendido (EKF)
## Vehicle Dynamics State Estimation via Extended Kalman Filter (EKF)

- **Categoria / Route:** `/projetos/motorsport-f1/102` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/102-vehicle-dynamics-state-estimation-via-extended-kalman-filter-ekf`
- **Benchmark de Referência:** `F1 Skill 02 — State Estimation (Vehicle Dynamics EKF)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack de referência originalmente anunciada:** não é evidência de importação/execução nesta implementação.
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
