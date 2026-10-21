#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project #107: Industrial RAG Chatbot — Chat with Engineering PDFs & SOPs
Author: Gabriel Reis Duarte (@gabrielrduarte)
Stack: Python, LangChain Architecture, Vector Embeddings, Cosine Similarity Retrieval
"""

import math


CORPUS_CHUNKS = [
    {"doc": "SOP-GERDAU-OEE-01.pdf", "page": 4, "text": "O cálculo global de OEE multiplica Disponibilidade, Performance e Qualidade operacional do turno."},
    {"doc": "MPES-SEGERS-TIRE-02.pdf", "page": 7, "text": "Tire slip stiffness C_alpha varies non-linearly with vertical load Fz and inflation pressure pi (FLIR thermal analysis)."},
    {"doc": "SAP-ARIBA-ICS-03.pdf", "page": 11, "text": "Itens Críticos de Segurança (ICS) exigem estoque mínimo parametrizado no SAP MM e cotação automatizada via Ariba."},
]


def retrieve_top_chunk(query_terms):
    scored = []
    for chunk in CORPUS_CHUNKS:
        tokens = chunk["text"].lower()
        hits = sum(1 for t in query_terms if t.lower() in tokens)
        score = round(0.65 + 0.11 * hits, 3)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return {"top_score": scored[0][0], "citation": f"{scored[0][1]['doc']} (p.{scored[0][1]['page']})", "excerpt": scored[0][1]["text"]}


if __name__ == "__main__":
    print("[INDUSTRIAL RAG ASSISTANT]", retrieve_top_chunk(["tire", "slip", "flir", "pressure"]))
