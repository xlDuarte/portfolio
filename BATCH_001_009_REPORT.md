# Execução verificável — lote 001–009 (Data Analysis)

- **Escopo:** 9 análises distintas, datasets gerados de forma determinística, fluxos de validação Pandas/NumPy, gráficos Matplotlib, notebooks Jupyter, CLI e documentos específicos.
- **Testes:** `python -m unittest discover -s tests -v` e execução real de cada `main.py`, mais testes negativos de domínio e validação de esquemas. Ver `tests/test_analytics_batch1.py`.
- **Artefatos:** `analytics_batch1/`, `site/cases/001/` … `/009/`; vídeos ou screenshots Power BI não gerados, porque Power BI Desktop não estava acessível.
- **Reprodução:** `python -m analytics_batch1.generate` deve reproduzir os mesmos CSVs (seed 20261021); `--report-dir` produz gráfico e métricas.
- **Interpretação:** estudo reproduzível com dados sintéticos NÃO é implantação industrial nem case com benefício econômico comprovado.
- **Critério pendente de 100%:** Power BI PBIP/PBIX válido, execução e screenshot no Power BI Desktop, fontes externas autorizadas, testes E2E reais e demais lotes #011–#111.
