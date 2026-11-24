> **Auditoria técnica #110:** Preserva modelagens numéricas e incorpora painel com varredura de rigidez, mapas térmicos artificiais e histograma de amortecedores. Não é FLIR nem o simulador proprietário ChassisSim. **Stack efetiva:** Python, NumPy, Pandas, Plotly, Streamlit. Dados fictícios, nenhuma telemetria de F1 ou inspeção industrial autêntica, nenhuma homologação externa.

## Execução comprovável

```bash
python -m pip install -r requirements/motorsport-core.txt
python -m streamlit run motorsport_batch/performance.py
```

**Código e testes:** [módulos executáveis](../../../motorsport_batch/README.md) e [suíte CI](../../../tests/test_motorsport_advanced.py). 

# Project #110 — Suíte Completa de Engenharia de Performance em Motorsport (Pneus, FLIR, Setup, HH Timing & Laptime Sim)
## Complete Motorsport Performance Engineering Suite (Tire Physics, FLIR, Setup, HH Timing & Laptime Sim)

- **Categoria / Route:** `/projetos/motorsport-f1/110` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim`
- **Benchmark de Referência:** `Flagship #110 — Full 5-Day Motorsport Performance Engineering Seminar Suite (Porsche Cup / WEC)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Tecnologias de benchmark:** referências aspiracionais, não necessariamente implementadas neste caso.
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Plataforma integral englobando todos os 5 dias do seminário de Engenharia de Performance (Jorge Segers / Porsche Cup Brasil): (1) Aquisição de Dados e Prioridades; (2) Física de Pneus, Sensibilidade à Carga C_alpha(Fz, pi), Termografia FLIR e Estratégia HH Timing; (3) Estilo de Pilotagem, Balanço Sub/Sobrevirante e Amortecedores; (4) Simulação de Tempo de Volta (ChassisSim LMP3/GT3) e Delta de Classificação; (5) Operação de Track Day.

## 2. Industrial & Motorsport Context (EN-US)
Comprehensive suite encompassing all 5 days of the Motorsport Performance Engineering Seminar (Jorge Segers / Porsche Cup Brasil): (1) Data Acquisition Priorities; (2) Tire Physics, Load Sensitivity C_alpha(Fz, pi), FLIR Thermal Photography & HH Timing Strategy; (3) Driver Style, Understeer/Oversteer Balance & Damper Histograms; (4) ChassisSim Laptime Simulation (LMP3/GT3) & Qualifying Lap Delta; (5) Track Day Operations.

## Cobertura Integral do PDF: *Motorsport Performance Engineering Seminar 2026 (Jorge Segers / Porsche Cup Brasil)*
- **Dia 1 (3 Dez — Quinta-Feira):** *Introduction, Required Accuracy in Motor Racing, Race Engineer Skills, Event Preparation, Paperwork & Regulations, Race Strategy, Data Acquisition Analysis Priorities & Metric-Based Performance Comparison*.
- **Dia 2 (4 Dez — Sexta-Feira):** *The Racecar Tire (Grip generation, Friction, Slip Angle $\alpha$ & Slip Ratio $\kappa$, Load Sensitivity $C_\alpha(F_z, p_i)$), Tire Pressure/Temperature/Wear, Practical Topic: FLIR Thermal Photography 3-Zone Analysis, Wet Weather Tires & HH Timing Strategy Case Study*.
- **Dia 3 (5 Dez — Sábado):** *Working with Drivers (Track Walks, Debriefing, Reporting, Radio Communication), Driving Line, Summarizing Driving Styles with Data, Quantifying Grip (Friction Circle) & Car Balance (Understeer/Oversteer), Race Car Setup & 4-Way Shock Absorbers (Low-Speed $<25\text{ mm/s}$ vs High-Speed $>25\text{ mm/s}$)*.
- **Dia 4 (6 Dez — Domingo):** *Practical Topic: Laptime Simulation with ChassisSim (LMP3 & Porsche GT3 Cup), Energy/Cell Voltage Surface, Race Strategy Review with HH Timing & Detailed Analysis of 2 Qualifying Laps by Different Drivers*.
- **Dia 5 (Temporada 2027 — Track Day Porsche Cup Brasil):** *Briefing com Engenheiro de Pista, Regulamento Técnico, Alocação de Pneus, Estratégia de Set-up e Processo Seletivo de Analista de Dados Porsche Carrera Cup*.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
