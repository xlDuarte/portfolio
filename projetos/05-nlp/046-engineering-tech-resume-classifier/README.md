# #46 — Engineering & Tech Resume Classifier

**Status:** classificação NLP com treinamento, teste e inferência reais sobre texto 100% sintético. Implementação: [motor NLP](../../../nlp_batch/engine.py); [templates artificiais](../../../nlp_batch/specs.json).

## Escopo efetivamente implementado
Identificação de áreas técnicas em currículos fictícios: dados, software, mecânica e automação. Não pontua candidatos nem toma decisões de recrutamento.

**Classes:** data, software, mechanical, automation.

**Tecnologia executada:** NLTK TweetTokenizer; Hugging Face Tokenizers WordPiece local (sem pesos de Transformers); Scikit-learn TF-IDF (caracteres e WordPiece), LogisticRegression e baseline DummyClassifier. Holdout isolado por *sentence template* (treino/calibração/teste = 3/1/1 templates por classe). Métricas: acurácia, macro-F1, relatório por classe e baseline.

## Reprodução
```bash
python -m pip install -r requirements-nlp.txt
python projetos/05-nlp/046-engineering-tech-resume-classifier/main.py --text "Experiência técnica com SQL dashboards e análise de dados" --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Saídas locais:** `nlp_batch/reports/46.json` e `nlp_batch/data/46.csv`. Não há download de modelos pré-treinados.

## Limitações
Templates sintéticos e variações contextuais não constituem observações independentes. Sem evidência de desempenho com dados reais, revisão de especialistas ou monitoramento em produção. A classificação de áreas profissionais não pode servir como avaliação individual, rejeição automática nem inferência sobre atributos pessoais.
