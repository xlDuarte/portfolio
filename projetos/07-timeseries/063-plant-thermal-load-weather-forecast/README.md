> **Atualização científica (fase 5a):** clima real de Taubaté (INMET A728) reconstruído hora a hora, radiação por Hargreaves–Samani e um galpão hipotético 1R1C com temperatura sol-ar. A cobertura domina: 236 MWh/ano de resfriamento com telha metálica escura contra 16 com telha sanduíche branca. Mann–Kendall em Taubaté e São Paulo não detecta tendência com 7 e 16 anos de dados. Código em [`energy/climate.py`](../../../energy/climate.py), método em [docs/physics/ENERGY.md](../../../docs/physics/ENERGY.md).

# #63 — Plant Thermal Load Weather Forecast

**Implementação:** série industrial semanal inteiramente sintética em kWh_thermal/week; modelos reais **Statsmodels ExponentialSmoothing (ETS)** e **Prophet**, comparados com baseline ingênuo sazonal. Sem dados corporativos, previsões oficiais ou evidência de benefício econômico.

## Contexto e método
Carga térmica industrial, não é previsão meteorológica real. O gerador de cenários produz série reproduzível de 240 observações semanais, com tendência, sazonalidade, ruído autocorrelacionado e mudança estrutural artificial.

Validação walk-forward com 3 origens de corte (168, 192 e 216 observações) e janelas de 8 semanas. Seleção somente entre baseline e ETS pelo MAE médio da validação. O Prophet é treinado efetivamente com os dados anteriores ao teste, comparado no holdout de 8 semanas sem influenciar a seleção. Intervalos são diagnósticos, **não calibrados para uso industrial**. Métricas: MAE, RMSE, WAPE, MAPE e sMAPE; Plotly exibe valores observados e previsões.

## Executar
```bash
python -m pip install -r requirements/timeseries.txt
python projetos/07-timeseries/063-plant-thermal-load-weather-forecast/main.py --save
python projetos/07-timeseries/063-plant-thermal-load-weather-forecast/main.py --future --save
python -m unittest discover -s tests -p test_timeseries_batch.py -v
```

**Arquivos gerados:** `timeseries_batch/data/63.csv`, `timeseries_batch/reports/63.json`, `timeseries_batch/reports/63_predictions.csv`, `timeseries_batch/reports/63_future.json` e `timeseries_batch/figures/63.html`. Fontes: [motor](../../../timeseries_batch/engine.py), [configuração](../../../timeseries_batch/config.json), [protocolo](../../../timeseries_batch/README.md).

## Limitações
Série inteiramente gerada por fórmula; não são observações industriais nem commodities/câmbio/energia de mercado. A acurácia sintética não demonstra generalização. Sem integração com APIs, ingestão real, monitoramento de drift, segmentação de ativos, avaliações de risco ou validação operacional.
