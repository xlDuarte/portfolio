# Projeto #017 — Industrial & Tech Talent Market EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Mapear tecnologias e salários anunciados em um mercado de vagas sintético.

## Metodologia implementada
Frequência de competências, salário mediano e distribuição por região.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/017.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 170 registros sintéticos. Esquema obrigatório: job_id, region, role, seniority, salary_monthly_brl, skills, posted_date. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements-eda.txt
python projetos/02-eda/017-industrial-tech-talent-market-eda/main.py
python projetos/02-eda/017-industrial-tech-talent-market-eda/main.py --report-dir /tmp/eda-017
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/017.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `postings`: 170
- `skills_frequency`: {'SAP': 61, 'Docker': 58, 'SQL': 57, 'Excel': 54, 'Power BI': 52, 'PLC': 51, 'Lean': 50, 'Statistics': 49, 'Pandas': 48, 'Spark': 46, 'AWS': 43, 'Pyth
- `salary_median_brl`: 10888.0
- `by_region`: [{'region': 'Campinas', 'postings': 59, 'mean_advertised_salary_brl': 10455.186440677966}, {'region': 'Vale do Paraiba', 'postings': 58, 'mean_adverti

## Riscos metodológicos
Não são vagas reais: não inferir salários nem disponibilidade no mercado atual.

## Recomendação operacional
Usar integração de dados reais com controle de data e deduplicação para apoiar contratação.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/017/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/017-industrial-tech-talent-market-eda)
