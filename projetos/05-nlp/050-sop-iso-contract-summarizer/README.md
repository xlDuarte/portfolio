# #050 — SOP, ISO & Contract Summarizer

**Status:** sumarizador extrativo operacional em documentos fornecidos pelo usuário ou exemplo fictício. As frases selecionadas permanecem literalmente iguais às do documento-fonte, acompanhadas do ID de cada sentença original.

## Funcionamento real
**spaCy** (`sentencizer`) segmenta frases; **Scikit-learn** (`TfidfVectorizer`, `cosine_similarity`) calcula centralidade e aplica seleção por diversidade MMR. O texto resultante não é gerado por modelo Transformer e não constitui análise jurídica nem resumo certificado de norma ISO.

## Execução
```bash
python -m pip install -r requirements/nlp.txt
python projetos/05-nlp/050-sop-iso-contract-summarizer/main.py --text-file nlp_batch/examples/sop.txt --save
python -m unittest discover -s tests -p test_nlp_batch.py -v
```

**Saída local:** `nlp_batch/reports/050.json` com `source_sentence_id`, `text` e `summary`. Código: [nlp_batch/engine.py](../../../nlp_batch/engine.py).

## Segurança e limites
Não foram incorporados textos protegidos por licença ISO. Não há modelo Hugging Face pré-treinado nem garantia de que obrigações, exceções, artigos legais, quantitativos e qualificações sejam preservados; é obrigatória revisão de especialista antes de uso decisório.
