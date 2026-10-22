> **Auditoria técnica #109:** Replay temporal Plotly/Streamlit a partir do simulador existente. Circuito é inspirado numa curva artificial, NÃO coordenadas GPS de Interlagos, e o tempo não é live timing F1. **Stack efetiva:** Simulador próprio Python, Plotly, Streamlit. Dados fictícios, nenhuma telemetria de F1 ou inspeção industrial autêntica, nenhuma homologação externa.

## Execução comprovável

```bash
python -m pip install -r requirements-motorsport-core.txt
python -m streamlit run motorsport_batch/replay.py
```

**Código e testes:** [módulos executáveis](../../../motorsport_batch/README.md) e [suíte CI](../../../tests/test_motorsport_advanced.py). 

# Project #109 — Motor de Replay de Corrida F1 & Telemetria GPS em Tempo Real (Construído do Zero)
## F1 Telemetry Race Replay & Live GPS Track Position Engine (Built from Scratch)

- **Categoria / Route:** `/projetos/motorsport-f1/109` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch`
- **Benchmark de Referência:** `Flagship #109 — Ground-Up 2D/3D Race Replay, Live Timing Tower & Delta Engine`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Tecnologias de benchmark:** referências aspiracionais, não necessariamente implementadas neste caso.
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Motor interativo construído 100% do zero para reconstrução e replay de corridas de F1 e Motorsport no mapa de pista (Interlagos), com torre de cronometragem ao vivo, compostos de pneus, zonas de DRS, telemetria sincronizada (Velocidade, RPM, Marcha, Acelerador, Freio) e comparador de delta entre pilotos.

## 2. Industrial & Motorsport Context (EN-US)
Interactive engine built 100% from scratch to reconstruct and replay F1 and Motorsport races on a live circuit map (Interlagos), featuring a live timing tower, tyre compounds, DRS zones, synchronized telemetry traces (Speed, RPM, Gear, Throttle, Brake), and multi-driver delta comparison.

## Arquitetura Construída 100% do Zero (Zero Código Copiado)
1. **Parametrização Geométrica de Circuito ($C(s)$):** Curvas harmônicas fechadas parametrizadas por comprimento de arco $s \in [0, 4309\text{ m}]$ reproduzindo os 3 setores, 15 curvas e 2 zonas de DRS do Autódromo de Interlagos.
2. **Solucionador Cinemático de Velocidade e Telemetria (20 Hz):** Calcula limite de aderência lateral $v_{\max}(s) = \sqrt{\mu_{\text{eff}} \cdot g / |\kappa(s)|}$, rampa de aceleração longitudinal, pressão de frenagem hidráulica (bar), marcha (1–8), RPM e acionamento de DRS.
3. **Torre de Cronometragem e Delta ($\Delta t$):** Sincroniza múltiplos carros em pista (F1, WEC Hypercar, Porsche 992 GT3 Cup) com desgaste dinâmico por composto (`SOFT`, `MEDIUM`, `HARD`, `INTER`).

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
