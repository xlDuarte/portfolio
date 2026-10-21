# Projeto #019 — Parts Dispatch & Lead-Time EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Auditar prazos de despacho e entrega de peças em rotas industriais.

## Metodologia implementada
Lead time total e p90 em horas, intervalo até despacho e pontualidade por SLA.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/019.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 190 registros sintéticos. Esquema obrigatório: order_id, origin, route, mode, order_created_utc, dispatched_utc, delivered_utc, promised_utc, quantity. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements-eda.txt
python projetos/02-eda/019-parts-dispatch-lead-time-eda/main.py
python projetos/02-eda/019-parts-dispatch-lead-time-eda/main.py --report-dir /tmp/eda-019
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/019.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `orders`: 190
- `median_dispatch_hours`: 8.0
- `p90_total_lead_hours`: 89.0
- `on_time_pct`: 66.32
- `by_route`: [{'route': 'SP-RJ', 'orders': 72}, {'route': 'SP-MG', 'orders': 61}, {'route': 'SP-PR', 'orders': 57}]

## Riscos metodológicos
Cronologia UTC validada, diferenças de datas calculadas com fusos coerentes.

## Recomendação operacional
Investigar gargalos por modal e rota antes de renegociar SLA.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/019/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/019-parts-dispatch-lead-time-eda)
