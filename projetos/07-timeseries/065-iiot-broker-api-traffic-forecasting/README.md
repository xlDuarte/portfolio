> **Status de implementação #065: PROTÓTIPO SINTÉTICO.** Este `main.py` apenas gera telemetria fabril fictícia e calcula estatísticas descritivas (OEE, temperatura e anomalias). As bibliotecas, modelos, ETL, APIs, visões computacionais e análises descritas neste documento representam **escopo proposto, não capacidades implementadas** neste script. Não há resultado industrial, acurácia ou desempenho real associado. Para casos analíticos reproduzíveis, veja [`case_studies/`](../../../case_studies/README.md).

# Project #065 — Previsão de Tráfego de Mensagens IIoT e APIs Corporativas
## IIoT Broker & API Traffic Forecasting

- **Categoria / Route:** `/projetos/timeseries/65` (`07 / 10`)
- **Diretório GitHub:** `projetos/07-timeseries/065-iiot-broker-api-traffic-forecasting`
- **Benchmark de Referência:** `65 Website Traffic Forecasting`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack proposta (não implementada no script):** `Pandas, Statsmodels, Prophet, Plotly`
- **Fluxo de Engenharia (How It Flows):** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE` (`Time Data -> Trend + Season -> Forecast -> MAPE Error`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Dimensionamento preditivo de throughput em brokers MQTT/Kafka e gateways de dados.

## 2. Industrial & Motorsport Context (EN-US)
Predictive throughput sizing for MQTT/Kafka brokers and enterprise data gateways.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
