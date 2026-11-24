# #43 — Regulatory & Supply Chain Alert Verifier

**Status:** pipeline NLP executável; exemplos e rótulos artificiais, sem validação real. Código de implementação: [nlp_batch/engine.py](../../../nlp_batch/engine.py); [especificação e templates](../../../nlp_batch/specs.json).

## Escopo e funcionalidade
Compara alegações a fontes textuais fornecidas, retorna IDs das fontes e indicação de concordância, conflito textual ou ausência de evidência; não verifica normas no mundo real.

**Implementação:** spaCy PhraseMatcher, tokenização Unicode e verificação de sobreposição textual, com indicação de fonte; a verificação é limitada à evidência fornecida.

## Executar
```bash
python -m pip install -r requirements/nlp.txt
python projetos/05-nlp/043-regulatory-supply-chain-alert-verifier/main.py --text "O comunicado fictício LOG-17 proíbe remessas de aço em junho." --save
python projetos/05-nlp/043-regulatory-supply-chain-alert-verifier/main.py --text "O comunicado fictício LOG-17 proíbe remessas de aço em junho." --evidence-file nlp_batch/examples/evidence.json
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Artefatos locais:** relatório JSON `nlp_batch/reports/43.json`.

## Limites
Concordância entre textos não determina verdade, autoridade normativa ou vigência. Documentos de exemplo são ficcionais. Nenhuma conclusão empresarial ou regulatória foi comprovada.
