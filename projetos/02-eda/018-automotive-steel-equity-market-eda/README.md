# Projeto #018 — Automotive & Steel Equity Market EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Estudar riscos e volatilidade em séries sintéticas de ações industriais.

## Metodologia implementada
Retornos log, volatilidade anualizada (252 pregões), drawdown e cobertura por ativo.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/018.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 756 registros sintéticos. Esquema obrigatório: ticker, date, close_brl, volume_shares. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements/eda.txt
python projetos/02-eda/018-automotive-steel-equity-market-eda/main.py
python projetos/02-eda/018-automotive-steel-equity-market-eda/main.py --report-dir /tmp/eda-018
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/018.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `quotes`: 756
- `instruments`: 3
- `volatility_by_symbol`: [{'ticker': 'AUTO_SYN', 'annualized_logreturn_vol_pct': 28.35, 'max_drawdown_pct': -38.71}, {'ticker': 'STEEL_SYN', 'annualized_logreturn_vol_pct': 30
- `coverage`: [{'ticker': 'AUTO_SYN', 'observations': 252, 'first_day': '2025-01-01', 'last_day': '2025-12-18'}, {'ticker': 'STEEL_SYN', 'observations': 252, 'first

## Riscos metodológicos
Preços gerados por random walk, não cotações; não fazer previsão de retorno.

## Recomendação operacional
Reproduzir em séries ajustadas reais apenas com fonte licenciada e tratamento de eventos corporativos.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/018/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/018-automotive-steel-equity-market-eda)
