# #47 — Shift-Log Criticality & Urgency NLP

**Status:** NLP real e executável. Triagem de relatos de turno por criticidade textual (baixa, média e alta). Nunca executar respostas emergenciais sem verificação humana.

**Implementação:** Classificação com NLTK, Hugging Face Tokenizers WordPiece (treinado localmente), TF-IDF de palavras/caracteres, Scikit-learn LogisticRegression e DummyClassifier.
**Classes:** low, medium, high. Separação entre templates de treino/calibração/teste (3/1/1) e relatórios por classe.

## Reprodução
```bash
python -m pip install -r requirements-nlp.txt
python projetos/05-nlp/047-shift-log-criticality-urgency-nlp/main.py --text "Rotina de inspeção concluída sem intercorrência" --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Saída local:** `nlp_batch/reports/47.json` e `nlp_batch/data/47.csv`. Código-fonte [nlp_batch/engine.py](../../../nlp_batch/engine.py).

## Limitações
Classificação em dados sintéticos não comprova capacidade de detecção de incidentes reais. Não há homologação de produção.
