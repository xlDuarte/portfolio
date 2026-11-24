# #75 — Stamped serial OCR

**Status:** funcionalidade de visão computacional real, com dados **inteiramente sintéticos**. OCR de códigos artificiais impressos (não marcação em metal real).

**Tecnologias utilizadas:** OpenCV + Tesseract; OpenCV e NumPy. Pré-processamento Otsu e pytesseract/Tesseract OCR recebem imagem sintética de texto impresso; não existe reconhecimento validado de punção em metal real.

## Executar
```bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements/vision.txt
python projetos/08-vision/075-stamped-serial-die-cast-ocr/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

Relatório em `vision_batch/reports/75.json` e PNG original artificial em `vision_batch/reports/75.png`. [Código](../../../vision_batch/engine.py) · [metodologia](../../../vision_batch/README.md).

**Limitações:** sem imagens de produção, teste em condições reais ou garantia de leitura/inspeção; sempre requer verificação humana.
