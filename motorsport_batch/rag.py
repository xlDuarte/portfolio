"""#107: PDF-backed LangChain chunking and extractive grounded retrieval (NO LLM).

A real PDF is generated as a fictional test fixture then parsed with pypdf.
LangChain Document/RecursiveCharacterTextSplitter/RunnableLambda are executed.
Scikit-learn TF-IDF retrieves evidence; response quotes matched source text
and cites filename and page. No provider APIs or model hallucinations.
"""
from pathlib import Path
import re
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CORPUS={
    "fictional-pump-maintenance.pdf":[
        "Synthetic pump maintenance SOP. Isolate power using lockout tagout before pump inspection. Record bearing vibration RMS every shift.",
        "For the fictional pump, inspect axial vibration when simulated RMS exceeds 6 mm/s. Human engineer authorizes corrective maintenance."
    ],
    "fictional-vehicle-setup.pdf":[
        "Synthetic race engineering note. Tire thermal inner center outer readings should be compared as a three zone profile before setup changes.",
        "Aerodynamic balance is a tradeoff between cornering downforce and straight line drag in a simplified lap simulation."
    ],
    "fictional-plant-quality.pdf":[
        "Synthetic quality control handbook. Traceability requires a lot identifier, inspection date, visual acceptance and review signature.",
        "An anomalous sensor reading is an alert for human review, not verified proof of machine failure."
    ]
}
def build_demo_pdfs(destination:str|Path)->list[Path]:
    from reportlab.pdfgen import canvas
    root=Path(destination);root.mkdir(parents=True,exist_ok=True)
    output=[]
    for name,pages in CORPUS.items():
        path=root/name
        doc=canvas.Canvas(str(path),pagesize=(595,842))
        for page in pages:
            words=page.split()
            lines=[];current=""
            for word in words:
                if len(current)+len(word)+1>75:
                    lines.append(current);current=word
                else:current=(current+" "+word).strip()
            lines.append(current)
            for i,line in enumerate(lines):doc.drawString(35,780-25*i,line)
            doc.showPage()
        doc.save();output.append(path)
    return output

def ingest_pdfs(paths:list[Path])->list[Document]:
    if not paths:raise ValueError("Provide existing PDF files")
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from pypdf import PdfReader
    docs=[]
    for path in paths:
        file=Path(path)
        if not file.exists() or file.suffix.lower()!=".pdf":raise ValueError("A readable PDF is required")
        reader=PdfReader(str(file))
        for p,page in enumerate(reader.pages,1):
            content=page.extract_text() or ""
            if content.strip():
                docs.append(Document(page_content=content,
                                     metadata={"filename":file.name,"page":p}))
    splitter=RecursiveCharacterTextSplitter(chunk_size=190,chunk_overlap=25)
    return splitter.split_documents(docs)

def answer(question:str,pdf_files:list[str|Path],top_k:int=3)->dict[str,Any]:
    if not isinstance(question,str) or len(question.strip())<5:raise ValueError("Question needs at least five chars")
    if not isinstance(top_k,int) or not 1<=top_k<=10:raise ValueError("top_k must be 1..10")
    docs=ingest_pdfs([Path(x) for x in pdf_files])
    if not docs:raise ValueError("No text found in supplied PDFs")
    vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words="english")
    matrix=vectorizer.fit_transform([d.page_content for d in docs]+[question])
    ranking=cosine_similarity(matrix[:-1],matrix[-1]).ravel()
    best=sorted(range(len(docs)),key=lambda i:(-ranking[i],docs[i].metadata["filename"],docs[i].metadata["page"]))[:top_k]
    evidence=[{"filename":docs[i].metadata["filename"],
               "page":docs[i].metadata["page"],
               "score":round(float(ranking[i]),6),
               "quote":re.sub(r"\s+"," ",docs[i].page_content.strip())[:190]}
              for i in best if ranking[i]>.005]
    return {"project_id":107,
            "question":question,
            "answer":(" ".join(f'[{e["filename"]} p.{e["page"]}] {e["quote"]}' for e in evidence)
                      if evidence else "No sufficiently similar PDF passages found."),
            "evidence":evidence,"retrieval":"LangChain PDF Documents and splitter; scikit-learn TF-IDF",
            "llm_called":False,"pdf_pages_extracted":len(docs),
            "limitations":"Extractive only. Relevance is lexical and synthetic PDFs are NOT corporate manuals."}

def runnable(files:list[str|Path]):
    from langchain_core.runnables import RunnableLambda
    return RunnableLambda(lambda question:answer(question,files))

def demo(output_dir:str|Path)->dict:
    files=build_demo_pdfs(output_dir)
    return runnable(files).invoke("How do I inspect pump bearing vibration?")
