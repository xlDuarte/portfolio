# #71 — Shop-floor PPE compliance

**Status:** código de visão computacional executável sobre **imagens sintéticas**; sem detecção certificada em ambientes reais.

## Funcionalidade implementada
Classificação visual de capacete em cenas artificiais.

**Tecnologia realmente utilizada neste projeto:** TensorFlow/Keras CNN. O módulo compartilhado usa OpenCV e NumPy. Executar com `--deep` treina uma CNN TensorFlow/Keras efetiva com imagens 100% artificiais, com teste gerado por seed separada.

## Execução
```bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements-vision.txt
python projetos/08-vision/071-shop-floor-ppe-compliance-detection/main.py --save
python -m pip install --no-cache-dir -r requirements-vision-deep.txt
python -m pip install --no-cache-dir 'torch==2.5.1+cpu' --index-url https://download.pytorch.org/whl/cpu
python projetos/08-vision/071-shop-floor-ppe-compliance-detection/main.py --deep --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

**Artefatos gerados:** imagem artificial PNG e relatório JSON em `vision_batch/reports/71.*` (não são métricas industriais observadas). Ver [métodos](../../../vision_batch/engine.py) e [critérios de aceitação](../../../vision_batch/README.md).

## Restrições
Sem imagens industriais reais, anotação independente, métricas de produção, medidas de privacidade ou homologação. Não usar como fiscalização de EPIs ou sistema de segurança.
