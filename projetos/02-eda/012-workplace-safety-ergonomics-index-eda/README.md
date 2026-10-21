# Projeto #012 — Workplace Safety & Ergonomics Index EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Analisar exposição, ergonomia e registros de segurança na produção.

## Metodologia implementada
Taxa de incidentes normalizada por 200 mil horas de exposição, segmentada por unidade.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/012.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 240 registros sintéticos. Esquema obrigatório: record_id, site, department, employee_hours, ergonomic_risk_score, safety_training_hours, reportable_incidents, near_misses. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements-eda.txt
python projetos/02-eda/012-workplace-safety-ergonomics-index-eda/main.py
python projetos/02-eda/012-workplace-safety-ergonomics-index-eda/main.py --report-dir /tmp/eda-012
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/012.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `incidents`: 41
- `total_exposure_hours`: 406979
- `incident_rate_per_200k_hours`: 20.15
- `ergonomic_risk_median`: 43.83
- `by_site`: [{'site': 'Assembly', 'incidents': 13, 'exposure_hours': 96381, 'near_misses': 42, 'incident_rate_per_200k_hours': 26.98}, {'site': 'Forge', 'incident

## Riscos metodológicos
Evitar confundir contagem absoluta com taxa: denominadores de exposição são necessários.

## Recomendação operacional
Investigar unidades com maior taxa e revisar a coleta de quase acidentes; associação não prova causalidade.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/012/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/012-workplace-safety-ergonomics-index-eda)
