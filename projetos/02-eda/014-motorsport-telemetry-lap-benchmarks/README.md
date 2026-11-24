# Projeto #014 — Motorsport Telemetry & Lap Benchmarks

**Status:** estudo de caso EDA reproduzível com **dados completamente sintéticos**. Não há integração com sistemas operacionais, mercado financeiro, registros de segurança reais ou telemetria oficial de automobilismo.

## Problema
Comparar desempenho de voltas por carro, composto e sessões em corrida.

## Metodologia implementada
Tempos por setor e volta, melhores voltas por carro e dispersão por composto.

Tecnologias **efetivamente utilizadas**: Pandas e NumPy para validação/cálculo; SQLite por consultas SQL via `sqlite3` e `pandas.read_sql_query`; Seaborn + Matplotlib para visualização SVG; Plotly para relatório HTML interativo (o JavaScript do Plotly depende da CDN na página exportada). Notebook Jupyter executa o mesmo código da CLI.

## Fonte de dados
`analytics_eda/data/014.csv` — criado por gerador com seed fixa (`analytics_eda/generate.py`). 180 registros sintéticos. Esquema obrigatório: lap_id, car, session, compound, lap_number, track_temp_c, sector_1_s, sector_2_s, sector_3_s. Duplicidades de chaves, campos nulos, negativos, não finitos ou incoerências específicas são rejeitados.

## Como reproduzir
A partir da raiz do repositório:
```bash
pip install -r requirements/eda.txt
python projetos/02-eda/014-motorsport-telemetry-lap-benchmarks/main.py
python projetos/02-eda/014-motorsport-telemetry-lap-benchmarks/main.py --report-dir /tmp/eda-014
python -m unittest discover -s tests -v
```
Relatório HTML interativo em `interactive.html` e gráfico acessível `chart.svg`. Notebook: `analytics_eda/notebooks/014.ipynb`.

## Saídas verificáveis (somente sintéticas)
- `laps`: 180
- `best_lap_s`: 81.972
- `median_lap_s`: 85.13
- `per_car`: [{'car': 'P01', 'laps': 24, 'best_lap_s': 81.972, 'avg_lap_s': 85.10441666666667}, {'car': 'P06', 'laps': 31, 'best_lap_s': 82.43499999999999, 'avg_la

## Riscos metodológicos
Setores somados geram tempo total; pista, sessão e composto confundem ranking.

## Recomendação operacional
Revisar setores mais variáveis com telemetria real e condições equivalentes.

## Limites
O estudo é executável, mas não demonstra impacto empresarial observado, dados externos, causalidade, machine learning treinado ou BI em Power BI. A página de resultados serve dados estáticos da execução auditada; a interface não está conectada a uma API em tempo real.

## Navegação
[Estudo publicado](https://gabriel-automotive-industrial-lab.vercel.app/cases/014/) · [Arquivos do projeto](https://github.com/xlDuarte/portfolio/tree/main/projetos/02-eda/014-motorsport-telemetry-lap-benchmarks)
