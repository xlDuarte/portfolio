# #49 — Multi-Plant Documentation Language Router

**Status:** NLP real e executável. Roteador PT/EN/ES para documentação industrial curta; sem tradução automática e sem depender de serviços externos.

**Implementação:** Classificação com NLTK, Hugging Face Tokenizers WordPiece (treinado localmente), TF-IDF de palavras/caracteres, Scikit-learn LogisticRegression e DummyClassifier.
**Classes:** pt, en, es. Separação entre templates de treino/calibração/teste (3/1/1) e relatórios por classe.

## Reprodução
```bash
python -m pip install -r requirements-nlp.txt
python projetos/05-nlp/049-multi-plant-documentation-language-router/main.py --text "Inspecionar os rolamentos antes do início do turno" --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Saída local:** `nlp_batch/reports/49.json` e `nlp_batch/data/49.csv`. Código-fonte [nlp_batch/engine.py](../../../nlp_batch/engine.py).

## Limitações
Classificador treinado em frases artificiais de três idiomas; não garante robustez para códigos, abreviações, misturas de idioma e documentos longos. Não há homologação de produção.
