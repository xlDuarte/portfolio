# Estratégia de pneus — projeto 101

Interface branca/ciano independente em `/cases/motorsport/101/`; o hub redireciona para a rota canônica. ECharts 6.0.0 usa a distribuição local já versionada em `../replay/vendor`, com licença no mesmo diretório. SVG mantém os gráficos disponíveis se a biblioteca falhar; o controle de parada é acessível por teclado.

`model.mjs` mantém `strategy()` do motor compartilhado intacto e decompõe os mesmos cálculos em voltas e stints. Busca limitada aos planos S–H e S–M–S. Soma por volta inclui pit loss ao fim da volta de parada. Degradação quadrática, referência fixa de combustível de 58 voltas, sem tráfego, clima, safety car ou inferência ML. Cada exportação inclui parâmetros, limitações, ranking e séries calculadas.

Validação: `node tests/strategy_checks.mjs` ou `python -m unittest discover -s tests -p test_strategy.py`. Verifica todas as combinações nos limites de distância/perda, paridade de tempos, stints, contagem de paradas e ótimo. Validação no navegador cobre gráficos, seleção, filtros, parâmetros, clique na janela, exportação, desktop, celular, tablet e fallback.
