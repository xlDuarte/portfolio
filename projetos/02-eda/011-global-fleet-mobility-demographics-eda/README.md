# Projeto #011 — Global Fleet & Mobility Demographics EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Analisar diferenças regionais no percentual de eletrificação de frota e sua evolução anual.

## Metodologia implementada
Calcular participação de veículos elétricos por região/ano e comparação no último ano.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/011.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 32 registros sintéticos. Esquema obrigatório: region, year, fleet_units, ev_units, population, urbanization_pct. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements-eda.txt
python projetos/02-eda/011-global-fleet-mobility-demographics-eda/main.py
python projetos/02-eda/011-global-fleet-mobility-demographics-eda/main.py --report-dir /tmp/eda-011
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/011.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `years`: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
- `regions`: 4
- `latest_year`: 2025
- `latest_ev_share_pct`: 11.315
- `prior_ev_share_pct`: 11.323
- `per_region`: [{'region': 'Asia', 'years': 8, 'last_year': 2025, 'reported_ev_observations': 26810730}, {'region': 'Europe', 'years': 8, 'last_year': 2025, 'reporte

## Riscos metodológicos
Usar volume ponderado de veículos elétricos, não média simples de percentuais regionais.

## Recomendação operacional
Priorizar planejamento de infraestrutura apenas como cenário sintético. Dados de frotas reais precisam ser incorporados.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/011/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/011-global-fleet-mobility-demographics-eda)
