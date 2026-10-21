# Projeto #020 — Critical Freight Delay Root-Cause EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Descrever e priorizar categorias de atraso de fretes críticos.

## Metodologia implementada
Pareto de minutos atrasados e gasto expresso associado por causa reportada.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/020.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 200 registros sintéticos. Esquema obrigatório: shipment_id, carrier, route, freight_mode, cause, delay_minutes, expedited_cost_brl, criticality. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements-eda.txt
python projetos/02-eda/020-critical-freight-delay-root-cause-eda/main.py
python projetos/02-eda/020-critical-freight-delay-root-cause-eda/main.py --report-dir /tmp/eda-020
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/020.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `shipments`: 200
- `delayed_shipments`: 153
- `total_delay_hours`: 260.57
- `expedite_cost_brl`: 1941194.23
- `cause_pareto`: [{'cause': 'Carrier', 'legs': 73, 'delay_minutes': 7265, 'expedite_cost_brl': 741610.21, 'cumulative_delay_share_pct': 46.47}, {'cause': 'Customs', 'l

## Riscos metodológicos
A classificação de causas já foi atribuída sinteticamente; não implica causalidade.

## Recomendação operacional
Investigar evidência documental e relações contratuais antes de concluir causa-raiz.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/020/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/020-critical-freight-delay-root-cause-eda)
