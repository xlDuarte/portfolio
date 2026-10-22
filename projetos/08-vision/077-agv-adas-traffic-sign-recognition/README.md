# #77 — AGV and ADAS sign recognition

**Implementação executável:** Reconhecimento de pictogramas artificiais por geometria e cor. A entrada de demonstração é imagem sintética criada por OpenCV; não houve teste industrial.

**Tecnologias efetivas:** OpenCV HSV + polígonos, NumPy. Segmentação HSV e aproximação poligonal identificam pictogramas artificiais; não há inferência adequada à navegação AGV ou direção ADAS.

## Executar
```bash
python -m pip install -r requirements-vision.txt
python projetos/08-vision/077-agv-adas-traffic-sign-recognition/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

Relatórios e imagens em `vision_batch/reports/77.json` e `vision_batch/reports/77.png`. [Motor](../../../vision_batch/engine.py), [documentação](../../../vision_batch/README.md).

**Limites:** apenas padrões desenhados artificialmente, sem métricas reais de acurácia, sem certificação, sem controles ou decisões automatizadas.
