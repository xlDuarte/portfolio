# #76 — Surface crack porosity and oxidation

**Status:** funcionalidade de visão computacional real, com dados **inteiramente sintéticos**. Segmentação de trincas, poros e manchas simuladas.

**Tecnologias utilizadas:** OpenCV threshold + componentes; OpenCV e NumPy. Segmentação de tons e geometria dos componentes de imagens artificiais de trincas, porosidade e oxidação; não equivale a ensaio não destrutivo.

## Executar
```bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements/vision.txt
python projetos/08-vision/076-surface-crack-oxidation-detection/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

Relatório em `vision_batch/reports/76.json` e PNG original artificial em `vision_batch/reports/76.png`. [Código](../../../vision_batch/engine.py) · [metodologia](../../../vision_batch/README.md).

**Limitações:** sem imagens de produção, teste em condições reais ou garantia de leitura/inspeção; sempre requer verificação humana.
