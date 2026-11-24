# #060 — Automated BOM & Maintenance Kit Engine

**Status:** motor funcional de listas de materiais para manutenção sobre BOM e estoque **100% sintéticos**. Não executa ordens de compra nem consulta SAP/Ariba.

## Escopo implementado
Explosão recursiva de conjuntos e subconjuntos, multiplicação por quantidade de equipamentos, verificação de integridade e ciclos, exigência de itens aprovados, cálculo de quantidades necessárias, subtração do estoque disponível, arredondamento por múltiplos de embalagem e estimativa de custo de reposição artificial. **O parâmetro `--top-k` não remove nenhum item obrigatório** da BOM.

**Stack efetiva:** Python e cálculos matemáticos de BOM; Pandas, NumPy e Scikit-learn são empregados em outros modelos do lote, não são necessários para o cálculo de BOM. Streamlit fornece visualização e filtros executáveis.

## Executar
```bash
python -m pip install -r requirements/recommendation.txt
python projetos/06-recommendation/060-automated-bom-maintenance-kit-engine/main.py --query PUMP-100 --filters-json '{"units":2,"pack_size":5}' --save
python -m streamlit run projetos/06-recommendation/060-automated-bom-maintenance-kit-engine/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Entradas**: BOMs, peças, quantidades, estoque, custos e aprovações da fixture [fixtures.json](../../../recommendation_batch/fixtures.json). **Saída:** JSON de componentes completos, shortfall e quantidade sugerida de reposição.

**Limitações:** manutenção, estoque e custo são fictícios. A correção de engenharia da lista de materiais, revisão do cadastro mestre, múltiplos reais de fornecimento e geração de pedidos permanecem fora da implementação. Nenhuma homologação industrial foi demonstrada.
