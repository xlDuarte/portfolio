# Project #009 — Avaliação de Ativos Industriais e Imobilizado (CAPEX)
## Industrial Asset & Facility Valuation

**Status:** estudo de caso executável sobre **dados 100% SINTÉTICOS**. Não é um projeto implantado, dado de SAP real, medição de valor realizado ou resultado empresarial mensurado.

## Objetivo e solução

Imobilizado: depreciação linear e valor presente de fluxos hipotéticos. Implementação específica no módulo compartilhado [`analytics_batch1/engine.py`](../../../analytics_batch1/engine.py) (função do projeto #009); não reutiliza o simulador genérico de OEE.

## Stack efetivamente executada

- **Python + Pandas + NumPy:** leitura CSV com esquema validado, transformação e métricas de negócio.
- **Matplotlib:** geração de gráfico SVG sob comando `--report-dir` (e SVG incluído no site).
- **Jupyter Notebook:** [notebook executável](../../../analytics_batch1/notebooks/009.ipynb), chama o mesmo motor validado.
- **Power BI:** **NÃO implementado como PBIX/PBIP testado**. Os arquivos `validated_data.csv` do relatório e as medidas descritas são apenas fontes preparatórias. Falta construir e validar o relatório no Power BI Desktop.

## Dados e fontes

O dataset versionado [`analytics_batch1/data/009.csv`](../../../analytics_batch1/data/009.csv) foi gerado deterministicamente com `numpy.random.default_rng(20261021)`. Representa um cenário artificial, sem dados pessoais/industriais reais. O esquema é verificado (chaves, tipos, faltantes, limites e invariantes específicas). Execute `python -m analytics_batch1.generate` para regenerar.

## Como executar

A partir da raiz do repositório:

```bash
pip install -r requirements/case-studies.txt
python projetos/01-dados/009-industrial-asset-facility-valuation/main.py
python projetos/01-dados/009-industrial-asset-facility-valuation/main.py --report-dir reports/009
python -m unittest discover -s tests -v
```

Para CSV próprio compatível:

```bash
python projetos/01-dados/009-industrial-asset-facility-valuation/main.py --source caminho/dados.csv
```

## Resultados verificáveis e limites

As métricas são **calculadas pelo código** sobre observações sintéticas; todos os números se referem apenas aos dados fictícios. Sem ensaios controlados ou dados de campo, **não** é possível inferir causalidade ou ganho econômico real. Metodologia e testes: [`analytics_batch1/README.md`](../../../analytics_batch1/README.md). Exibição de demonstração: [página #009](../../../site/cases/009/index.html).

## Próximo passo de produção

Conectar dados de origem autorizados, conferir regras com área responsável, versionar as evidências de refresh, criar relatório Power BI verificável e executar homologação em contexto industrial.
