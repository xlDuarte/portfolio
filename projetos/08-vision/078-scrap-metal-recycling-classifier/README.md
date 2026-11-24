# #78 — Scrap metal category classifier

**Implementação executável:** Classificação por histograma de cores de sucata fictícia. A entrada de demonstração é imagem sintética criada por OpenCV; não houve teste industrial.

**Tecnologias efetivas:** OpenCV color histogram, NumPy. Histogramas de cor com comparação cosseno ranqueiam amostras simuladas; cor não verifica composição química de metais.

## Executar
```bash
python -m pip install -r requirements/vision.txt
python projetos/08-vision/078-scrap-metal-recycling-classifier/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

Relatórios e imagens em `vision_batch/reports/78.json` e `vision_batch/reports/78.png`. [Motor](../../../vision_batch/engine.py), [documentação](../../../vision_batch/README.md).

**Limites:** apenas padrões desenhados artificialmente, sem métricas reais de acurácia, sem certificação, sem controles ou decisões automatizadas.
