# #45 — Technical Inspection Report Polarity

**Status:** classificação NLP com treinamento, teste e inferência reais sobre texto 100% sintético. Implementação: [motor NLP](../../../nlp_batch/engine.py); [templates artificiais](../../../nlp_batch/specs.json).

## Escopo efetivamente implementado
Classificação textual de laudos como conforme ou não conforme. Não substitui inspeção metrológica.

**Classes:** conforming, nonconforming.

**Tecnologia executada:** NLTK TweetTokenizer; Hugging Face Tokenizers WordPiece local (sem pesos de Transformers); Scikit-learn TF-IDF (caracteres e WordPiece), LogisticRegression e baseline DummyClassifier. Holdout isolado por *sentence template* (treino/calibração/teste = 3/1/1 templates por classe). Métricas: acurácia, macro-F1, relatório por classe e baseline.

## Reprodução
```bash
python -m pip install -r requirements/nlp.txt
python projetos/05-nlp/045-technical-inspection-report-polarity/main.py --text "Laudo registra conformidade dimensional da amostra" --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Saídas locais:** `nlp_batch/reports/45.json` e `nlp_batch/data/45.csv`. Não há download de modelos pré-treinados.

## Limitações
Templates sintéticos e variações contextuais não constituem observações independentes. Sem evidência de desempenho com dados reais, revisão de especialistas ou monitoramento em produção. 
