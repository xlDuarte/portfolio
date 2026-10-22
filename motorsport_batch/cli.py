"""Project-specific CLI for #104–#108.

Default --inspect runs deterministic domain input checks without requiring huge
ML dependencies; --run genuinely trains/executes the advertised libraries.
Outputs never contain made-up benchmark scores or connected company data.
"""
from pathlib import Path
import argparse
import json
import tempfile
import numpy as np

ROOT=Path(__file__).resolve().parent

def execute(project:int,run:bool=False,out_dir:str|Path|None=None):
    if project not in range(104,109):
        raise ValueError("Expected project #104–#108")
    if project==104:
        from .vibration import sequences
        a,b=sequences()
        result=({"project_id":104,"normal_sequences":len(a),"fault_sequences":len(b),
                 "sample_width":int(a.shape[1]),"source":"synthetic vibration"}
                if not run else __import__("motorsport_batch.vibration",fromlist=["evaluate"]).evaluate())
    elif project==105:
        from .xray import sample
        a,mask=sample(True,105)
        result=({"project_id":105,"synthetic_image_shape":list(a.shape),
                 "ground_truth_void_pixels":int(mask.sum()),"source":"synthetic X-ray image"}
                if not run else __import__("motorsport_batch.xray",fromlist=["evaluate"]).evaluate())
        if out_dir:
            import cv2
            folder=Path(out_dir);folder.mkdir(exist_ok=True,parents=True)
            cv2.imwrite(str(folder/"105-synthetic-xray.png"),(255*a).astype("uint8"))
    elif project==106:
        from .mlops import fabricate,population_stability_index
        if run:
            from .mlops import run as ml_run
            target=Path(out_dir) if out_dir else ROOT/"reports"/"mlflow-106"
            result=ml_run(target)
        else:
            x,y=fabricate()
            result={"project_id":106,"synthetic_samples":len(y),
                    "positive_labels":int(y.sum()),
                    "psi_synthetic_shift":round(population_stability_index(x[:,0],x[:,0]+.2),5),
                    "mlflow_run_created":False}
    elif project==107:
        from .rag import CORPUS
        if run:
            from .rag import demo
            target=Path(out_dir) if out_dir else ROOT/"reports"/"synthetic-pdfs-107"
            result=demo(target)
        else:
            result={"project_id":107,"available_fictional_pdfs":sorted(CORPUS),
                    "retrieval_executed":False,
                    "to_execute_pdf_parse_and_langchain":"--run"}
    else:
        from .explain import generate
        if run:
            from .explain import evaluate
            result=evaluate()
        else:
            x,y=generate()
            result={"project_id":108,"synthetic_rows":len(y),
                    "minority_rows":int(min(y.sum(),len(y)-y.sum())),
                    "smote_shap_executed":False}
    result.setdefault("source","entirely synthetic; no production claims")
    result["requested_full_execution"]=bool(run)
    if out_dir:
        output=Path(out_dir);output.mkdir(exist_ok=True,parents=True)
        # Grad-CAM heatmaps are large; retain numeric truth in JSON for CI.
        (output/f"{project:03d}.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def main(project:int|None=None):
    p=argparse.ArgumentParser(description="Actually implement motorsport/industrial model workflows")
    if project is None:p.add_argument("project",type=int,choices=list(range(104,109)))
    p.add_argument("--run",action="store_true",help="Fit full frameworks and produce held-out evidence")
    p.add_argument("--output",type=str)
    args=p.parse_args()
    pnum=project if project is not None else args.project
    print(json.dumps(execute(pnum,args.run,args.output),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
