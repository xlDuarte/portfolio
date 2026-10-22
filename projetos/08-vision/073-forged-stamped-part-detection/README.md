# #73 — Forged and stamped part counting

**Status:** código de visão computacional executável sobre **imagens sintéticas**; sem detecção certificada em ambientes reais.

## Funcionalidade implementada
Detecção e contagem de peças não sobrepostas em imagens sintéticas.

**Tecnologia realmente utilizada neste projeto:** OpenCV findContours. O módulo compartilhado usa OpenCV e NumPy. Não há generalização demonstrada para câmeras industriais.

## Execução
```bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements-vision.txt
python projetos/08-vision/073-forged-stamped-part-detection/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

**Artefatos gerados:** imagem artificial PNG e relatório JSON em `vision_batch/reports/73.*` (não são métricas industriais observadas). Ver [métodos](../../../vision_batch/engine.py) e [critérios de aceitação](../../../vision_batch/README.md).

## Restrições
Sem imagens industriais reais, anotação independente, métricas de produção, medidas de privacidade ou homologação. Não usar para ações automatizadas de segurança ou qualidade.
