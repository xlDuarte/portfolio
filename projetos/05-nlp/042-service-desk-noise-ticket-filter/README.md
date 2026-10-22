# #42 — Service Desk Noise & Ticket Filter

**Status:** pipeline NLP executável; exemplos e rótulos artificiais, sem validação real. Código de implementação: [nlp_batch/engine.py](../../../nlp_batch/engine.py); [especificação e templates](../../../nlp_batch/specs.json).

## Escopo e funcionalidade
Distingue publicidade/ruído de chamados técnicos acionáveis; não apaga chamados automaticamente.

**Implementação:** NLTK TweetTokenizer, tokenizador Hugging Face WordPiece treinado localmente, TF-IDF e Scikit-learn LogisticRegression, com baseline DummyClassifier, treinamento em templates distintos e holdout separado.

**Classes:** noise, actionable. Treino/calibração/teste por template (3/1/1), métricas macro-F1, acurácia e relatório por classe.

## Executar
```bash
python -m pip install -r requirements-nlp.txt
python projetos/05-nlp/042-service-desk-noise-ticket-filter/main.py --text "Mensagem promocional com desconto de assinatura" --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Artefatos locais:** relatório JSON `nlp_batch/reports/42.json`; dataset sintético CSV `nlp_batch/data/42.csv`.

## Limites
Vocabulário e classes artificiais; ausência de anotações independentes, avaliação externa, robustez adversarial e aferição em produção. Nenhuma conclusão empresarial ou regulatória foi comprovada.
