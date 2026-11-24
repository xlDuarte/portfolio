# #79 — Plant yard vehicle multi-object tracking

**Escopo implementado:** Rastreamento multiobjeto simples de caixas móveis artificiais. Imagens exclusivamente artificiais.

**Tecnologias efetivas:** OpenCV centroids/association com OpenCV e NumPy. Detecção e rastreamento de caixas artificiais ao longo de quadros; IDs não identificam veículos ou pessoas reais.

## Execução
```bash
python -m pip install -r requirements/vision.txt
python projetos/08-vision/079-plant-yard-vehicle-fleet-tracking/main.py --save
python -m unittest discover -s tests -p test_vision_batch.py -v
```

JSON e imagem demonstrativa `vision_batch/reports/79.json`, `vision_batch/reports/79.png`. [Motor](../../../vision_batch/engine.py) · [metodologia](../../../vision_batch/README.md).

**Limitação:** sem base real e sem validação externa; não serve como vigilância, identificação de pessoas, classificação metalúrgica de produção ou fundamento decisório.
