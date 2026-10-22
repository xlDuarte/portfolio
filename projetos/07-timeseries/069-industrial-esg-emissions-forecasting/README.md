# #69 — Industrial ESG Emissions Forecasting

**Status:** motor de previsão executável; observações são 100% sintéticas, métricas não constituem acurácia de produção.

## Escopo concluído
Emissões industriais simuladas, não medições auditadas. Unidade alvo: **tCO2e/week**. Série determinística, semanal, com 240 registros; controles para valores negativos, buracos e duplicidades temporais e limite de 100% para ocupação (#067).

**Técnica:** Statsmodels ETS (tendência, sazonalidade semanal de período 13), Prophet (com sazonalidade anual), NumPy/Pandas, gráficos Plotly e baseline sazonal ingênuo. Backtest expanding-window em 168, 192, 216 observações e 8 semanas por origem; holdout intocado de 8 semanas finais. Seleção de baseline ou ETS pelo MAE da validação e avaliação adicional do Prophet sem selecionar pelo teste. Inclui MAE, RMSE, WAPE, MAPE e sMAPE e cálculo descritivo de cobertura de intervalos.

## Executar
```bash
python -m pip install -r requirements-timeseries.txt
python projetos/07-timeseries/069-industrial-esg-emissions-forecasting/main.py --save
python projetos/07-timeseries/069-industrial-esg-emissions-forecasting/main.py --future --save
python -m unittest discover -s tests -p test_timeseries_batch.py -v
```

**Arquivos:** dados `timeseries_batch/data/69.csv`, relatório `timeseries_batch/reports/69.json`, previsões `timeseries_batch/reports/69_predictions.csv`, futuro `timeseries_batch/reports/69_future.json`, gráfico `timeseries_batch/figures/69.html` (Plotly offline).

**Limitações:** gerador artificial, ausência de dados autorizados reais, benchmarking de produção, atualizações de fonte, auditoria ESG, APIs climáticas ou cambiais; uso depende de validação e controles do domínio.
