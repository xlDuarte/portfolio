# Industrial NLP case studies #041–#050

This directory replaces ten numeric telemetry stubs with **actual text processing**, without claiming real industrial training data.

| ID | Implemented behavior | Actual technology |
|---|---|---|
| 041 | Warranty sentiment: negative, neutral, positive | TF-IDF + Logistic Regression |
| 042 | Service-desk actionable issue versus promotional noise | TF-IDF + Logistic Regression |
| 043 | Regulatory/supply-chain claim consistency against **supplied** documents with document IDs | spaCy PhraseMatcher + normalized token overlap |
| 044 | SAP PM work-order domain/topic (mechanical/electrical/automation/quality) | TF-IDF + Logistic Regression |
| 045 | Inspection report polarity (conforming/nonconforming) | TF-IDF + Logistic Regression |
| 046 | Technical-domain taxonomy for fictional résumés (not hiring/ranking) | TF-IDF + Logistic Regression |
| 047 | Shift-log urgency for manual triage (low/medium/high) | TF-IDF + Logistic Regression |
| 048 | Compliance/governance language patterns with excerpts and qualified context | spaCy PhraseMatcher |
| 049 | PT/EN/ES short industrial document language router | multilingual character n-grams + Logistic Regression |
| 050 | Traceable extractive document summary, returning source sentence IDs | spaCy sentencizer + Scikit-learn TF-IDF/MMR |

## Reproducible execution

```bash
python -m pip install -r requirements/nlp.txt
python -m unittest discover -s tests -p 'test_nlp_batch.py' -v
python -m nlp_batch.engine 41 --text "Falha repetida na garantia"
python -m nlp_batch.engine 43 --text "O comunicado fictício LOG-17 proíbe remessas de aço em junho."
python -m nlp_batch.engine 50 --text-file examples/sop.txt
python -m nlp_batch.engine 49 --save
```

All entrypoints under `projetos/05-nlp/<ID>-*/main.py` accept `--text`, `--text-file`, `--save`; #043 also supports `--evidence-file` with `[{"id":"DOC-1","text":"..."}]`.

## Models and validation protocol

Projects #041/#042/#044/#045/#046/#047/#049 generate domain-specific, labeled **synthetic** text. Five distinct sentence templates per class are separated **by template**, not by row: three templates for training, one for calibration diagnostics, one for untouched test. Synthetic context variations can repeat across classes and do not represent independent real-world cases. The baseline is `DummyClassifier`; the trained model is `TfidfVectorizer` (local Hugging Face `tokenizers` WordPiece tokenizer, initially trained **only on train** using NLTK `TweetTokenizer`) plus character n-gram TF-IDF and Scikit-learn `LogisticRegression`. The saved report contains holdout accuracy, macro-F1 and per-class classification report. Calibration split reports macro-F1; it is not used for hyperparameter selection here.

#043 compares supplied claim text with locally supplied evidence; a consistent label means *only textual consistency*, never verification of a real regulation, source authority or truth. #048 is a rule-based inspection, not a finding of wrongdoing; negation is shallow and requires human confirmation. #050 is **extractive**, not an abstractive Hugging Face transformer: every generated summary sentence is copied from an input sentence and includes a source sentence ID. References to ISO in project titles do not imply copies of proprietary ISO standards.

## Threats to validity / exclusions

No customer, employee, salary, health or recruiting data were used. The fixtures are simple, templated and lack independent annotations, linguistic robustness, genuine adversarial tests, business validation, model monitoring, drift evidence, or legal approval. **Do not automate rejection of job applicants, regulatory conclusions, safety escalation or compliance sanctions using these demonstrations.** Human-review workflows are required.

`--save` exports generated CSV for supervised tasks to `nlp_batch/data/{ID}.csv` and JSON reports to `nlp_batch/reports/{ID}.json`; these are local, regenerated artifacts.
