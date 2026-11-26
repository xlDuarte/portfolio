> **Atualização científica (fase 5b):** balanço de massa do banho químico (decomposição e arraste de primeira ordem, reação por área tratada), estimação por mínimos quadrados sobre a solução exata e política de reposição (s, S) por simulação. Com uma faixa estreita de concentração arraste e reação não se separam (correlação −0,998), mas o consumo total sai com ±0,15 %; ignorar a variância do prazo do fornecedor derruba o serviço de 99 % para 86 %. Dados sintéticos. Método em [docs/physics/THERMAL.md](../../../docs/physics/THERMAL.md).

# #70 — Consumables Burn-Rate Forecasting

**Status:** motor de previsão executável; observações são 100% sintéticas, métricas não constituem acurácia de produção.

## Escopo concluído
Consumo de fluidos e gases industriais fictícios. Unidade alvo: **litres/week**. Série determinística, semanal, com 240 registros; controles para valores negativos, buracos e duplicidades temporais e limite de 100% para ocupação (#067).

**Técnica:** Statsmodels ETS (tendência, sazonalidade semanal de período 13), Prophet (com sazonalidade anual), NumPy/Pandas, gráficos Plotly e baseline sazonal ingênuo. Backtest expanding-window em 168, 192, 216 observações e 8 semanas por origem; holdout intocado de 8 semanas finais. Seleção de baseline ou ETS pelo MAE da validação e avaliação adicional do Prophet sem selecionar pelo teste. Inclui MAE, RMSE, WAPE, MAPE e sMAPE e cálculo descritivo de cobertura de intervalos.

## Executar
```bash
python -m pip install -r requirements/timeseries.txt
python projetos/07-timeseries/070-consumables-burn-rate-forecasting/main.py --save
python projetos/07-timeseries/070-consumables-burn-rate-forecasting/main.py --future --save
python -m unittest discover -s tests -p test_timeseries_batch.py -v
```

**Arquivos:** dados `timeseries_batch/data/70.csv`, relatório `timeseries_batch/reports/70.json`, previsões `timeseries_batch/reports/70_predictions.csv`, futuro `timeseries_batch/reports/70_future.json`, gráfico `timeseries_batch/figures/70.html` (Plotly offline).

**Limitações:** gerador artificial, ausência de dados autorizados reais, benchmarking de produção, atualizações de fonte, auditoria ESG, APIs climáticas ou cambiais; uso depende de validação e controles do domínio.
