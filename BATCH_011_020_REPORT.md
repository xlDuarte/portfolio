# Lote 011–020 — 10 estudos EDA

O template de OEE foi substituído em cada projeto por métricas específicas, 10 CSVs sintéticos, 10 notebooks, 10 SVGs e 10 páginas Plotly.

Todos os indicadores são **calculados sobre dados sintéticos**; sem alegação de resultados reais, causalidade, APIs live, datasets externos, Power BI ou validação de negócio.

Tecnologias executadas: Pandas, NumPy, consultas SQL (sqlite3), Seaborn, Matplotlib, Plotly.

Testes: `python -m unittest discover -s tests -v` e notebooks Jupyter com `nbclient`.

**Pendente:** inspeção E2E em navegador real, dados operacionais/financeiros licenciados e revisão metodológica externa por domínio.

## Evidência de validação (21 de outubro de 2026)

- 38/38 testes automatizados da suíte completa em ambiente local: aprovados.
- 111/111 scripts main.py executados sem erro; todos passaram em análise sintática.
- 10/10 notebooks executados pelo nbclient (o último foi repetido isoladamente após limite do ambiente).
- 10/10 relatórios: métricas JSON, SVG Seaborn/Matplotlib e Plotly HTML gerados.
- Cinco HTMLs principais: JavaScript passou em `node --check`.
- A execução de testes E2E do navegador não foi possível: Chromium não está instalado no Playwright do ambiente.
- Interatividade Plotly utiliza CDN, mantendo SVG estático como fallback disponível na mesma página.
- GitHub CI precisa instalar requirements-eda.txt; workflow atualizado.

**Estado de aceite:** aplicação demonstrativa e cálculo sintético reproduzível. Ainda não há verificação com dados reais, métricas de negócio observadas ou validação E2E em navegador.
