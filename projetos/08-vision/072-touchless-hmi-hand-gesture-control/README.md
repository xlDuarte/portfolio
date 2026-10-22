# #72 — Touchless HMI gesture control

**Status:** código de visão computacional executável sobre **imagens sintéticas**; sem detecção certificada em ambientes reais.

## Funcionalidade implementada
Classificação de silhuetas de gestos por correspondência de contornos.

**Tecnologia realmente utilizada neste projeto:** OpenCV matchShapes. O módulo compartilhado usa OpenCV e NumPy. Não há generalização demonstrada para câmeras industriais.

## Execução
```bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements-vision.txt
python projetos/08-vision/072-touchless-hmi-hand-gesture-control/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

**Artefatos gerados:** imagem artificial PNG e relatório JSON em `vision_batch/reports/72.*` (não são métricas industriais observadas). Ver [métodos](../../../vision_batch/engine.py) e [critérios de aceitação](../../../vision_batch/README.md).

## Restrições
Sem imagens industriais reais, anotação independente, métricas de produção, medidas de privacidade ou homologação. Os comandos HMI são apenas descrições, nunca acionamentos.
