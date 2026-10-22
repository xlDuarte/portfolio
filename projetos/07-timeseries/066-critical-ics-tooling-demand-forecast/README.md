# #66 — Critical ICS & Tooling Demand Forecast

**Status técnico:** previsão sobre série **inteiramente sintética** em units/week com treino real de **Statsmodels ETS** e **Prophet**, além de baseline sazonal.

## O que funciona
Demanda de ferramentas e insumos críticos não observada. Gerador determinístico de 240 semanas, tendência, sazonalidade de 13 e 52 semanas, ruído estocástico simulado e mudança estrutural artificial.

**Backtesting:** origens 168/192/216, horizonte fixo de 8 semanas, sem acesso a dados de teste na seleção. Seleção baseline sazonal versus ETS pelo MAE médio de validação. Prophet realmente ajustado apenas ao treino, acompanhado de previsões/intervalos diagnósticos no teste final. Métricas calculadas: MAE, RMSE, WAPE, MAPE (com denominador protegido) e sMAPE. Plotly gera gráfico HTML com previsões e série de teste.

## Reproduzir
```bash
python -m pip install -r requirements-timeseries.txt
python projetos/07-timeseries/066-critical-ics-tooling-demand-forecast/main.py --save
python projetos/07-timeseries/066-critical-ics-tooling-demand-forecast/main.py --future --save
python -m unittest discover -s tests -p test_timeseries_batch.py -v
```

**Arquivos locais:** `timeseries_batch/data/66.csv`, `timeseries_batch/reports/66.json`, `timeseries_batch/reports/66_predictions.csv`, `timeseries_batch/reports/66_future.json`, `timeseries_batch/figures/66.html`. [Código compartilhado](../../../timeseries_batch/engine.py) · [parâmetros por projeto](../../../timeseries_batch/config.json).

**Restrições:** dados simulados, nenhuma inferência confiável em operação; ausência de telemetria real, fontes externas, contrato de qualidade dos dados, atualização automática e modelo validado para decisões de produção.
