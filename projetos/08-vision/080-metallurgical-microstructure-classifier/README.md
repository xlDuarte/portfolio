# #80 — Metallurgical microstructure classifier

**Escopo implementado:** CNN PyTorch treinada sobre texturas metalográficas fictícias. Imagens exclusivamente artificiais.

**Tecnologias efetivas:** PyTorch Conv2d com OpenCV e NumPy. Convolução real em PyTorch Conv2D treinada em texturas geradas matematicamente. Executar `--deep` ajusta parâmetros da CNN, calcula loss e probabilidades em amostras de seed separada, sem dados microscópicos verdadeiros.

## Execução
```bash
python -m pip install -r requirements-vision.txt
python projetos/08-vision/080-metallurgical-microstructure-classifier/main.py --save
python -m pip install -r requirements-vision-deep.txt
python projetos/08-vision/080-metallurgical-microstructure-classifier/main.py --deep --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

JSON e imagem demonstrativa `vision_batch/reports/80.json`, `vision_batch/reports/80.png`. [Motor](../../../vision_batch/engine.py) · [metodologia](../../../vision_batch/README.md).

**Limitação:** sem base real e sem validação externa; não serve como vigilância, identificação de pessoas, classificação metalúrgica de produção ou fundamento decisório.
