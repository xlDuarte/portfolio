# Projeto #016 — SMED & High-Speed Setup Telemetry EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Comparar tempos de troca rápida de ferramentas antes e após SMED.

## Metodologia implementada
Duração total, mediana por fase e análise por tipo de troca.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/016.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 120 registros sintéticos. Esquema obrigatório: changeover_id, asset, operation, phase, internal_setup_min, external_setup_min, production_run_hours, operator_count. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements/eda.txt
python projetos/02-eda/016-smed-high-speed-setup-telemetry-eda/main.py
python projetos/02-eda/016-smed-high-speed-setup-telemetry-eda/main.py --report-dir /tmp/eda-016
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/016.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `changeovers`: 120
- `median_before_min`: 29.01
- `median_after_min`: 27.13
- `median_reduction_pct`: 6.48
- `by_operation_phase`: [{'operation': 'Die', 'phase': 'After', 'events': 23, 'mean_setup_min': 25.56}, {'operation': 'Die', 'phase': 'Before', 'events': 18, 'mean_setup_min'

## Riscos metodológicos
Amostras antes/depois não são pareadas; não se trata de estimativa causal.

## Recomendação operacional
Priorizar padronização de setups e replicar estudo com pareamento por SKU.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/016/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/016-smed-high-speed-setup-telemetry-eda)
