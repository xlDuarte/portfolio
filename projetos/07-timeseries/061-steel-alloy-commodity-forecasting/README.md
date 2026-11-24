# #61 — Steel & Alloy Commodity Forecasting

**Implementação:** série industrial semanal inteiramente sintética em BRL/tonne; modelos reais **Statsmodels ExponentialSmoothing (ETS)** e **Prophet**, comparados com baseline ingênuo sazonal. Sem dados corporativos, previsões oficiais ou evidência de benefício econômico.

## Contexto e método
Sazonalidade contratual e volatilidade simulada de aço e ligas. O gerador de cenários produz série reproduzível de 240 observações semanais, com tendência, sazonalidade, ruído autocorrelacionado e mudança estrutural artificial.

Validação walk-forward com 3 origens de corte (168, 192 e 216 observações) e janelas de 8 semanas. Seleção somente entre baseline e ETS pelo MAE médio da validação. O Prophet é treinado efetivamente com os dados anteriores ao teste, comparado no holdout de 8 semanas sem influenciar a seleção. Intervalos são diagnósticos, **não calibrados para uso industrial**. Métricas: MAE, RMSE, WAPE, MAPE e sMAPE; Plotly exibe valores observados e previsões.

## Executar
```bash
python -m pip install -r requirements/timeseries.txt
python projetos/07-timeseries/061-steel-alloy-commodity-forecasting/main.py --save
python projetos/07-timeseries/061-steel-alloy-commodity-forecasting/main.py --future --save
python -m unittest discover -s tests -p test_timeseries_batch.py -v
```

**Arquivos gerados:** `timeseries_batch/data/61.csv`, `timeseries_batch/reports/61.json`, `timeseries_batch/reports/61_predictions.csv`, `timeseries_batch/reports/61_future.json` e `timeseries_batch/figures/61.html`. Fontes: [motor](../../../timeseries_batch/engine.py), [configuração](../../../timeseries_batch/config.json), [protocolo](../../../timeseries_batch/README.md).

## Limitações
Série inteiramente gerada por fórmula; não são observações industriais nem commodities/câmbio/energia de mercado. A acurácia sintética não demonstra generalização. Sem integração com APIs, ingestão real, monitoramento de drift, segmentação de ativos, avaliações de risco ou validação operacional.
