# #48 — Compliance & Governance Text Scanner

**Status:** NLP real e executável. Scanner auditável de expressões indicativas de controle interno ou demanda de revisão; destaca trechos e posições por spaCy PhraseMatcher, inclusive qualificação de negação na janela anterior.

**Implementação:** spaCy PhraseMatcher com códigos internos, detecção contextual limitada de proibição/negação e trechos referenciados por offsets de tokens.


## Reprodução
```bash
python -m pip install -r requirements/nlp.txt
python projetos/05-nlp/048-compliance-governance-text-scanner/main.py --text "Foi reportado compartilhamento de senha. É proibido conflito de interesses." --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Saída local:** `nlp_batch/reports/48.json`. Código-fonte [nlp_batch/engine.py](../../../nlp_batch/engine.py).

## Limitações
A marcação de padrões não identifica violação, responsabilização ou cumprimento efetivo de normas. Não há homologação de produção.
