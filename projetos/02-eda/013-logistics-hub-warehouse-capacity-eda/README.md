# Projeto #013 — Logistics Hub & Warehouse Capacity EDA

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Identificar gargalos de capacidade de pallets e docas em centros de distribuição.

## Metodologia implementada
Ocupação de posições e horas de doca; contagem de snapshots acima de 90%.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/013.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 144 registros sintéticos. Esquema obrigatório: snapshot_id, hub, date, capacity_pallets, occupied_pallets, inbound_pallets, outbound_pallets, dock_hours_used, dock_hours_available. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements/eda.txt
python projetos/02-eda/013-logistics-hub-warehouse-capacity-eda/main.py
python projetos/02-eda/013-logistics-hub-warehouse-capacity-eda/main.py --report-dir /tmp/eda-013
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/013.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `snapshots`: 144
- `mean_occupancy_pct`: 72.06
- `near_capacity_count`: 30
- `mean_dock_utilisation_pct`: 52.14
- `by_hub`: [{'hub': 'Hub-RJ', 'snapshots': 43, 'avg_occupancy_pct': 74.05650055370985}, {'hub': 'Hub-MG', 'snapshots': 45, 'avg_occupancy_pct': 72.55639417989418

## Riscos metodológicos
A ocupação é medida pontual; não se pode somar a capacidade de snapshots como se fosse estoque único.

## Recomendação operacional
Analisar janelas de pico e redistribuição de docas após integrar WMS real.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/013/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/013-logistics-hub-warehouse-capacity-eda)
