"""Project #32: Vendor B2B Credit Approval. Reproducible synthetic ML workflow."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from classification_batch.engine import evaluate
if __name__=="__main__":print(json.dumps(evaluate(32),indent=2))
