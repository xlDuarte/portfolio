"""Industrial NLP #041-#050: trained text models and evidence-preserving document tools.

Every fixture is artificial. No downloaded transformer weights, industrial observations,
external regulatory verification, recruiting decisions or measured economic impact.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from nltk.tokenize import TweetTokenizer
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from tokenizers import Tokenizer, models, pre_tokenizers, trainers
from spacy.matcher import PhraseMatcher

ROOT = Path(__file__).resolve().parent
SPECS = {int(k): v for k, v in json.loads((ROOT / "specs.json").read_text(encoding="utf-8")).items()}
CLASSIFIERS = {k for k, v in SPECS.items() if v["kind"] == "classifier"}
NLTK_TOKENIZER = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)

def normalize(text: str) -> str:
    """Unicode-aware lowercasing while preserving semantic negation tokens."""
    return unicodedata.normalize("NFKC", text).strip().lower()

def valid_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip() or len(text) > 50000:
        raise ValueError("Text must be non-empty and at most 50000 characters")
    return text.strip()

def make_dataset(project: int, variants: int = 12, seed: int = 2026) -> pd.DataFrame:
    """Artificial, labeled text: distinct sentence templates for train/cal/test."""
    if project not in CLASSIFIERS:
        raise ValueError("Only classification projects generate labeled fixtures")
    if not isinstance(variants, int) or not 6 <= variants <= 100:
        raise ValueError("variants must be an integer in [6,100]")
    rng = np.random.default_rng(seed + project)
    cfg = SPECS[project]
    rows = []
    for label, templates in cfg["labels"].items():
        if len(templates) != 5:
            raise ValueError("Exactly five disjoint templates required per label")
        for template_index, phrase in enumerate(templates):
            split = ("train" if template_index < 3 else "calibration" if template_index == 3 else "test")
            for replicate in range(variants):
                unit = rng.choice(["planta norte", "planta sul", "centro técnico", "unidade leste"])
                asset = rng.choice(["linha A", "linha B", "célula C", "área D"])
                shift = rng.choice(["manhã", "tarde", "noite"])
                # Deliberately non-predictive context, equally distributed over labels.
                text = f"{phrase}. Contexto: {unit}, {asset}, turno {shift}, protocolo {replicate:03d}."
                rows.append({
                    "sample_id": f"{project:03d}-{label}-{template_index}-{replicate:03d}",
                    "template_id": f"{label}:{template_index}",
                    "split": split, "text": text, "label": label,
                    "source": "synthetic template, not a customer or employee record",
                })
    return pd.DataFrame(rows)

def validate_frame(project: int, frame: pd.DataFrame) -> None:
    cfg = SPECS[project]
    required = {"sample_id", "template_id", "split", "text", "label"}
    if not required.issubset(frame.columns) or len(frame) < 60:
        raise ValueError("Required fields absent or insufficient rows")
    if frame[list(required)].isna().any().any() or frame.sample_id.duplicated().any():
        raise ValueError("Missing fields or duplicated sample IDs")
    if set(frame.label) != set(cfg["labels"]):
        raise ValueError("Target classes do not match project taxonomy")
    if set(frame.split) != {"train", "calibration", "test"}:
        raise ValueError("Expected train/calibration/test splits")
    for a in ("train", "calibration", "test"):
        if set(frame.loc[frame.split == a, "label"]) != set(cfg["labels"]):
            raise ValueError("Missing class in split " + a)
    groups = {s: set(frame.loc[frame.split == s, "template_id"]) for s in ("train", "calibration", "test")}
    if any(groups[a] & groups[b] for a, b in (("train", "calibration"), ("train", "test"), ("calibration", "test"))):
        raise ValueError("Template leakage across splits")
    if any(not isinstance(t, str) or not t.strip() for t in frame.text):
        raise ValueError("Invalid text")

def train_classifier(project: int, frame: pd.DataFrame | None = None):
    if project not in CLASSIFIERS:
        raise ValueError("Not a supervised text classification task")
    frame = make_dataset(project) if frame is None else frame.copy()
    validate_frame(project, frame)
    train = frame[frame.split == "train"]
    calibration = frame[frame.split == "calibration"]
    test = frame[frame.split == "test"]
    # NLTK + Hugging Face Tokenizers: WordPiece tokenizer FIT ON TRAIN ONLY.
    hf = Tokenizer(models.WordPiece(unk_token="[UNK]"))
    hf.pre_tokenizer = pre_tokenizers.Whitespace()
    hf.train_from_iterator(
        (" ".join(NLTK_TOKENIZER.tokenize(t)) for t in train.text),
        trainer=trainers.WordPieceTrainer(vocab_size=1600, min_frequency=1, special_tokens=["[UNK]"]),
    )
    def hf_tokens(text: str) -> list[str]:
        return hf.encode(" ".join(NLTK_TOKENIZER.tokenize(text))).tokens
    feats = FeatureUnion([
        ("wordpiece", TfidfVectorizer(tokenizer=hf_tokens, token_pattern=None, lowercase=False,
                                      ngram_range=(1, 2), sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=2,
                                 max_features=12000, sublinear_tf=True)),
    ])
    baseline = DummyClassifier(strategy="most_frequent").fit(
        train[["text"]], train.label)
    model = Pipeline([
        ("features", feats),
        ("classifier", LogisticRegression(max_iter=1200, random_state=2026, class_weight="balanced")),
    ])
    model.fit(train.text, train.label)
    # Calibration is a distinct, unseen-template evaluation; no test-based tuning.
    cal_prediction = model.predict(calibration.text)
    prediction = model.predict(test.text)
    labels = sorted(SPECS[project]["labels"])
    result = {
        "project_id": project,
        "project": SPECS[project]["title"],
        "status": "trained on SYNTHETIC text, not validated on real documents",
        "split": "disjoint text templates by label (3 train/1 calibration/1 test)",
        "train_rows": int(len(train)), "calibration_rows": int(len(calibration)),
        "test_rows": int(len(test)),
        "classes": labels,
        "baseline_test_accuracy": round(float(accuracy_score(test.label, baseline.predict(test[["text"]]))), 4),
        "calibration_macro_f1": round(float(f1_score(calibration.label, cal_prediction, average="macro")), 4),
        "test_accuracy": round(float(accuracy_score(test.label, prediction)), 4),
        "test_macro_f1": round(float(f1_score(test.label, prediction, average="macro")), 4),
        "test_classification_report": classification_report(test.label, prediction, labels=labels, output_dict=True, zero_division=0),
        "actual_tools": ["NLTK TweetTokenizer", "Hugging Face tokenizers.WordPiece (trained locally)",
                         "Scikit-learn TF-IDF", "Scikit-learn LogisticRegression"],
        "limitations": "Synthetic labeled sentences, only held-out templates; no independent human annotations, pretrained HF transformer, or production suitability.",
    }
    return model, result, frame

def _plain_terms(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", normalize(text))
    folded = "".join(c for c in normalized if not unicodedata.combining(c))
    stopwords = {"o", "a", "as", "os", "um", "uma", "de", "da", "do", "na", "no", "em", "para", "que",
                 "com", "dos", "das", "ao", "antes", "the", "and", "is", "of", "to", "nao", "sem"}
    return {w for w in re.findall(r"[a-z0-9]+", folded) if len(w) > 1 and w not in stopwords}

def _negative(text: str) -> bool:
    return bool(re.search(r"\b(não|nao|not|never|sem)\b", normalize(text)))

DEFAULT_EVIDENCE = [
    {"id": "SOP-FX01", "text": "O procedimento fictício SOP-FX01 exige inspeção de válvulas antes da partida do forno."},
    {"id": "LOG-17", "text": "O comunicado fictício LOG-17 não proíbe remessas de aço em junho."},
]
DEFAULT_ALERTS = [
    "O procedimento fictício SOP-FX01 exige inspeção de válvulas antes da partida do forno.",
    "O comunicado fictício LOG-17 proíbe remessas de aço em junho.",
    "A regra ZZ-80 exige desligar todos os equipamentos sem registro de evidência.",
]
def verify_alert(alert: str, evidence: list[dict]) -> dict:
    """Matches only supplied documents, not external law or ground truth."""
    alert = valid_text(alert)
    if not isinstance(evidence, list):
        raise ValueError("Evidence must be a list")
    nlp = spacy.blank("pt")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    candidates = []
    for rec in evidence:
        if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not isinstance(rec.get("text"), str):
            raise ValueError("Evidence entries must include string id and text")
        doc_id, source = valid_text(rec["id"]), valid_text(rec["text"])
        matcher.add(doc_id, [nlp.make_doc(doc_id)])
        intersection = _plain_terms(alert) & _plain_terms(source)
        union = _plain_terms(alert) | _plain_terms(source)
        similarity = len(intersection) / max(1, len(union))
        # Explicit document reference is useful, but cannot alone establish support.
        source_ref_match = any(nlp.vocab.strings[match] == doc_id
                               for match, _, _ in matcher(nlp.make_doc(alert)))
        candidates.append((similarity, source_ref_match, rec))
    if not candidates:
        return {"status": "insufficient_evidence", "source_ids": [], "overlap_score": 0.0}
    score, ref_match, best = max(candidates, key=lambda t: (t[0], t[1]))
    if score < 0.40 or not ref_match:
        status = "insufficient_evidence"
        ids = []
    else:
        status = ("conflicting_supplied_text" if _negative(alert) != _negative(best["text"])
                  else "consistent_with_supplied_text")
        ids = [best["id"]]
    return {"status": status, "source_ids": ids, "overlap_score": round(float(score), 4),
            "scope": "textual consistency with caller-supplied synthetic sources; no legal/factual verification"}

CONTROL_PATTERNS = {
    "SEGREGATION": ["segregação de funções", "segregacao de funcoes"],
    "DOCUMENTATION": ["pagamento sem nota fiscal", "compra sem documento"],
    "ACCESS": ["compartilhamento de senha", "senha compartilhada"],
    "CONFLICT": ["conflito de interesses", "interesse pessoal na compra"],
}
def scan_governance(text: str) -> dict:
    """Auditable matching, not a legal conclusion or a compliance certification."""
    text = valid_text(text)
    nlp = spacy.blank("pt")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for code, phrases in CONTROL_PATTERNS.items():
        matcher.add(code, [nlp.make_doc(p) for p in phrases])
    doc = nlp(text)
    findings = []
    for match_id, start, end in matcher(doc):
        window = doc[max(0, start - 5):start].text.lower()
        # Negation or prohibitions signal presence of a written control, not a proven incident.
        qualified = bool(re.search(r"\b(não|nao|nunca|vedado|proibido|proibida|impedir)\b", window))
        findings.append({
            "control": nlp.vocab.strings[match_id],
            "excerpt": doc[start:end].text,
            "token_start": start,
            "token_end": end,
            "triage": "control_language_detected" if qualified else "human_review",
        })
    return {"findings": findings, "count": len(findings),
            "status": "textual pattern scanner, not a legal compliance decision"}

DEMO_DOCUMENT = (
    "O procedimento interno fictício determina a inspeção de válvulas antes da partida do forno. "
    "O operador deve registrar a pressão hidráulica no checklist de turno. "
    "O supervisor revisa registros de manutenção preventiva toda sexta-feira. "
    "A ausência de inspeção deve ser comunicada à equipe de segurança. "
    "A liberação do equipamento exige assinatura do responsável técnico. "
    "O documento não constitui norma ISO oficial."
)
def summarize_document(text: str, max_sentences: int = 3) -> dict:
    """Extract sentences verbatim, with stable source sentence IDs."""
    text = valid_text(text)
    if not isinstance(max_sentences, int) or max_sentences < 1 or max_sentences > 12:
        raise ValueError("max_sentences must be in [1, 12]")
    nlp = spacy.blank("xx")
    nlp.add_pipe("sentencizer")
    sentences = [s.text.strip() for s in nlp(text).sents if s.text.strip()]
    if len(sentences) == 0:
        raise ValueError("No sentences found")
    if len(sentences) <= max_sentences:
        chosen = list(range(len(sentences)))
    else:
        vector = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode").fit_transform(sentences)
        sim = cosine_similarity(vector)
        relevance = sim.mean(axis=1)
        chosen = []
        while len(chosen) < max_sentences:
            remaining = [i for i in range(len(sentences)) if i not in chosen]
            def score(i):
                redundancy = max((sim[i, j] for j in chosen), default=0.0)
                return .7 * float(relevance[i]) - .3 * float(redundancy)
            chosen.append(max(remaining, key=lambda i: (score(i), -i)))
        chosen.sort()
    selected = [{"source_sentence_id": f"S{i+1:03d}", "text": sentences[i]} for i in chosen]
    return {
        "method": "extractive TF-IDF MMR, spaCy sentence segmentation",
        "sentence_count": len(sentences),
        "summary": " ".join(s["text"] for s in selected),
        "source_sentences": selected,
        "limitations": "No abstractive transformer; extracted sentences do not establish legal accuracy or completeness",
    }

def run(project: int, text: str | None = None, evidence: list[dict] | None = None, save: bool = False) -> dict:
    if project not in SPECS:
        raise ValueError("Unknown project")
    cfg = SPECS[project]
    if project in CLASSIFIERS:
        model, result, frame = train_classifier(project)
        if text is not None:
            original = valid_text(text)
            result["inference"] = {"text": original, "predicted_class": str(model.predict([original])[0]),
                                   "confidence_note": "No calibrated probability or production assurance"}
    elif project == 43:
        claims = [valid_text(text)] if text is not None else DEFAULT_ALERTS
        result = {"project_id": project, "claims": [{"claim": c, **verify_alert(c, DEFAULT_EVIDENCE if evidence is None else evidence)} for c in claims]}
    elif project == 48:
        result = {"project_id": project, **scan_governance(text if text is not None else
                  "Foi reportado compartilhamento de senha na unidade. É proibida a segregação de funções?")}
    elif project == 50:
        result = {"project_id": project, **summarize_document(text if text is not None else DEMO_DOCUMENT)}
    else:
        raise AssertionError("Unknown task")
    result["data_origin"] = "synthetic examples and/or caller-provided text"
    result["independently_validated"] = False
    if save:
        (ROOT / "reports").mkdir(exist_ok=True)
        (ROOT / "reports" / f"{project:03d}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if project in CLASSIFIERS:
            (ROOT / "data").mkdir(exist_ok=True)
            frame.to_csv(ROOT / "data" / f"{project:03d}.csv", index=False)
    return result

def cli(project: int | None = None):
    parser = argparse.ArgumentParser(description="Industrial NLP demonstrations on artificial data")
    if project is None:
        parser.add_argument("project", type=int, choices=sorted(SPECS))
    parser.add_argument("--text", type=str, default=None)
    parser.add_argument("--text-file", type=Path, default=None)
    parser.add_argument("--evidence-file", type=Path, default=None,
                        help="JSON array of {id,text} evidence records; #043 only")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    if args.text is not None and args.text_file is not None:
        parser.error("Use --text OR --text-file")
    text = args.text_file.read_text(encoding="utf-8") if args.text_file else args.text
    evidence = json.loads(args.evidence_file.read_text(encoding="utf-8")) if args.evidence_file else None
    if evidence is not None and (project if project is not None else args.project) != 43:
        parser.error("--evidence-file only applies to project 43")
    print(json.dumps(run(project if project is not None else args.project,
                         text=text, evidence=evidence, save=args.save),
                     ensure_ascii=False, indent=2))
if __name__ == "__main__":
    cli()
