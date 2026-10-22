# Executar os projetos localmente

[README](../README.md) · [111 projetos](../PROJECT_CATALOG.md) · [Auditoria](../INTEGRATION_AUDIT.md)

## Requisitos

- Python **3.11**, Git e ambiente virtual.
- GitHub Actions usa Linux Ubuntu; alguns componentes exigem Tesseract, Docker, dependências pesadas, CPU/memória ou instalações locais.
- **Não** forneça senhas empresariais, credenciais de SAP/Ariba, chaves de API, documentos internos ou telemetria proprietária.

```bash
git clone https://github.com/xlDuarte/portfolio.git
cd portfolio
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-integration.txt
python scripts/audit_integrated_portfolio.py --check
python -m unittest discover -s tests -v
```

**Nota:** o repositório pode estar privado, exigindo autorização para clonar. O Pages publica apenas HTML, não acesso ao código privado.

## Entrypoints por área

| Área | Comando | Observação |
|---|---|---|
| Regressão | `python -m regression_batch.engine 22 --save` | Modelos em dados simulados |
| Classificação | `python -m classification_batch.engine 31` | Rótulos gerados artificialmente |
| NLP | `python -m nlp_batch.engine 41` | Consultar argumentos do módulo |
| Visão | `python -m unittest discover -s tests -p test_vision_batch.py -v` | OCR/TensorFlow/PyTorch podem precisar de runtimes separados |
| BI e finanças | `python -m business_batch.engine 82 --save` | SQL SQLite; nenhum Power BI Desktop executado |
| Plataforma API | `uvicorn advanced_batch.api:app --host 127.0.0.1 --port 8000` | API local somente, sintética |
| Motorsport ML | `python -m motorsport_batch.cli 108 --run` | Exige `requirements-motorsport-mlops.txt` |
| Física/replay | `python -m streamlit run motorsport_batch/replay.py` | Geometria de circuito sintética |

Dependências adicionais por caso: `requirements-vision-deep.txt`, `requirements-motorsport-tf.txt` e `requirements-motorsport-mlops.txt`. Leia o README específico antes de executar o treinamento completo.

## O que a execução comprova

Um resultado válido depende de código realmente executado, testes, separação de treino/teste, métricas reproduzíveis e limitações explícitas. Arquivos `.dax`, nomes de bibliotecas, dashboards ilustrativos e dados simulados **não** comprovam experiência em sistemas industriais conectados, nem fazem do GitHub Pages um servidor Python.

Veja a matriz individual em [TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv](../TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv).
