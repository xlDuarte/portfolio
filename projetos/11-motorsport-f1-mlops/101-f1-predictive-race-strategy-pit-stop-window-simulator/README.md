> **Auditoria do lote #101–#110:** Modelos XGBoost e RandomForestRegressor ajustados em voltas artificiais agrupadas por sessão; simulador físico original de pit-stop preservado. **Tecnologias comprováveis neste projeto:** Python, Scikit-learn, XGBoost, NumPy, Pandas; simulador matemático de stint. Todos os resultados e testes são sintéticos, sem dados reais F1 ou indústria, sem homologação de produção. As demais tecnologias citadas no benchmark não estão implícitas neste projeto.

## Como executar a implementação atual

```bash
python -m pip install -r requirements-motorsport-core.txt
python projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator/main.py --fit-ml
python -m unittest discover -s tests -p test_motorsport_batch.py -v
```

**Evidência técnica:** [pacote de implementação](../../../motorsport_batch/README.md), [código especializado](../../../motorsport_batch/) e [testes avançados](../../../tests/test_motorsport_advanced.py). 

# Project #101 — Estratégia Preditiva de Corrida (F1) & Simulador de Janela de Pit-Stop
## F1 Predictive Race Strategy & Pit-Stop Window Simulator

- **Categoria / Route:** `/projetos/motorsport-f1/101` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator`
- **Benchmark de Referência:** `F1 Skill 01 — Predictive Race Strategy (XGBoost / Random Forest)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack de referência originalmente anunciada:** não é evidência de importação/execução nesta implementação.
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
