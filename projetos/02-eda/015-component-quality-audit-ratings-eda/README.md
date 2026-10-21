# Projeto #015 — Component Quality Audit Ratings EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Medir qualidade de fornecedores e lotes de componentes.

## Metodologia implementada
Taxa ponderada de defeitos por unidade inspecionada e Pareto por fornecedor.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/015.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 180 registros sintéticos. Esquema obrigatório: batch_id, supplier, part_family, inspected_units, defect_units, rating_1to5, audit_date. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements-eda.txt
python projetos/02-eda/015-component-quality-audit-ratings-eda/main.py
python projetos/02-eda/015-component-quality-audit-ratings-eda/main.py --report-dir /tmp/eda-015
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/015.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `batches`: 180
- `defects`: 1172
- `inspected`: 30882
- `weighted_defect_rate_pct`: 3.795
- `by_supplier`: [{'supplier': 'Supplier-B', 'defects': 319, 'inspected': 7783, 'defect_rate_pct': 4.1}, {'supplier': 'Supplier-D', 'defects': 305, 'inspected': 8042, 

## Riscos metodológicos
Não substituir taxa ponderada por média de percentuais de lotes desiguais.

## Recomendação operacional
Focar inspeções nos grupos prioritários após ajuste de mix e amostragem.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/015/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/015-component-quality-audit-ratings-eda)
