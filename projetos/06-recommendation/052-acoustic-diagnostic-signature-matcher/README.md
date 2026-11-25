> **Atualização científica (fase 4a):** correspondência de assinaturas de defeito no domínio da ordem com vibração real do CWRU. Em outra carga, 75 % de acerto balanceado em ordens contra 28 % em Hz; pista interna reconhecida em 100 % das janelas, inclusive em rolamento nunca visto. Código em [`bearings/signatures.py`](../../../bearings/signatures.py), método em [docs/physics/BEARINGS.md](../../../docs/physics/BEARINGS.md).

# #52 — Acoustic Diagnostic Signature Matcher

**Status:** funcionalidade específica executável, com entradas e dados exclusivamente sintéticos; não é prova de performance em produção.

## Escopo implementado
Sinais de vibração artificiais processados com FFT e características espectrais (RMS, frequência dominante, energia por banda). NearestNeighbors aproxima assinaturas de falhas; não representa diagnóstico acústico clínico/industrial real.

**Ferramentas reais:** Python, Pandas, NumPy, Scikit-learn (NearestNeighbors) e interface Streamlit.

**Código:** [motor](../../../recommendation_batch/engine.py) · [catálogo fictício](../../../recommendation_batch/fixtures.json) · [métodos e restrições](../../../recommendation_batch/README.md).

## Executar
```bash
python -m pip install -r requirements/recommendation.txt
python projetos/06-recommendation/052-acoustic-diagnostic-signature-matcher/main.py --query "bearing_fault" --save
python -m streamlit run projetos/06-recommendation/052-acoustic-diagnostic-signature-matcher/streamlit_app.py
python -m unittest discover -s tests -p test_recommendation_batch.py -v
```

**Saída:** JSON com IDs, escore ou distância, justificativa e filtros; relatório salvo em `recommendation_batch/reports/52.json` se solicitado. Para FFT, são sinais gerados matematicamente com ruído artificial, não gravações de máquinas.
