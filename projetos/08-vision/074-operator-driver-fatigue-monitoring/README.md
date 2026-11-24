# #74 — Operator vigilance visual cue

**Status:** código de visão computacional executável sobre **imagens sintéticas**; sem detecção certificada em ambientes reais.

## Funcionalidade implementada
Indicador PERCLOS de abertura ocular em desenhos, sem inferir fadiga real.

**Tecnologia realmente utilizada neste projeto:** OpenCV imagem temporal. O módulo compartilhado usa OpenCV e NumPy. Não processa rostos de pessoas reais e não infere identidade ou emoção; a proporção de quadros com olhos fechados é apenas uma simulação demonstrativa.

## Execução
```bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements/vision.txt
python projetos/08-vision/074-operator-driver-fatigue-monitoring/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

**Artefatos gerados:** imagem artificial PNG e relatório JSON em `vision_batch/reports/74.*` (não são métricas industriais observadas). Ver [métodos](../../../vision_batch/engine.py) e [critérios de aceitação](../../../vision_batch/README.md).

## Restrições
Sem imagens industriais reais, anotação independente, métricas de produção, medidas de privacidade ou homologação. É inadequado para monitoramento de trabalhadores ou conclusões sobre fadiga.
