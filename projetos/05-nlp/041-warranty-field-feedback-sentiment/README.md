# #41 — Warranty & Field Feedback Sentiment

**Status:** pipeline NLP executável; exemplos e rótulos artificiais, sem validação real. Código de implementação: [nlp_batch/engine.py](../../../nlp_batch/engine.py); [especificação e templates](../../../nlp_batch/specs.json).

## Escopo e funcionalidade
Classifica satisfação e reclamações de garantia em três polaridades; use como triagem, nunca indicador real de satisfação.

**Implementação:** NLTK TweetTokenizer, tokenizador Hugging Face WordPiece treinado localmente, TF-IDF e Scikit-learn LogisticRegression, com baseline DummyClassifier, treinamento em templates distintos e holdout separado.

**Classes:** negative, neutral, positive. Treino/calibração/teste por template (3/1/1), métricas macro-F1, acurácia e relatório por classe.

## Executar
```bash
python -m pip install -r requirements-nlp.txt
python projetos/05-nlp/041-warranty-field-feedback-sentiment/main.py --text "Cliente relata falha repetida na garantia e solicita substituição" --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Artefatos locais:** relatório JSON `nlp_batch/reports/41.json`; dataset sintético CSV `nlp_batch/data/41.csv`.

## Limites
Vocabulário e classes artificiais; ausência de anotações independentes, avaliação externa, robustez adversarial e aferição em produção. Nenhuma conclusão empresarial ou regulatória foi comprovada.
