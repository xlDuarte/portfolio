# Automotive & Industrial Engineering Lab

**Portfólio técnico de Data Analytics, Machine Learning, Business Intelligence, Engenharia Industrial e Motorsport.**

[<ins>Explorar o portfólio web</ins>](https://xlduarte.github.io/portfolio/) · [111 projetos](PROJECT_CATALOG.md) · [Auditoria de tecnologias](TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv) · [Como executar](docs/GETTING_STARTED.md)

[![CI integrado — 111 projetos](https://github.com/xlDuarte/portfolio/actions/workflows/ci-and-pages.yml/badge.svg?branch=main)](https://github.com/xlDuarte/portfolio/actions/workflows/ci-and-pages.yml)
[![Publicação GitHub Pages](https://github.com/xlDuarte/portfolio/actions/workflows/ci-and-pages.yml/badge.svg?branch=main)](https://github.com/xlDuarte/portfolio/actions)
[Releases](https://github.com/xlDuarte/portfolio/releases) · [Packages](https://github.com/xlDuarte?tab=packages)

**Autor:** Gabriel Reis Duarte · [LinkedIn](https://www.linkedin.com/in/gabrielrduarte) · [GitHub](https://github.com/xlDuarte)

> **Transparência técnica:** os conjuntos de dados, sensores, corridas, documentos e fluxos operacionais demonstrados no portfólio são **sintéticos ou de teste**, salvo indicação e proveniência verificável em um projeto específico. Os testes automatizados demonstram execução de código em ambiente controlado, **não desempenho operacional ou integração com SAP, Ariba, MES, Power BI Desktop ou telemetria oficial da F1**. O projeto **#111 (F1 Predictive Intelligence Platform)** permanece parcialmente implementado. Este repositório **não está homologado 100/100**.

## Visão geral

O repositório contém **111 projetos numerados** e organizados em 11 áreas. Os casos trazem, conforme o projeto, scripts Python, consultas SQL, modelos treinados, dados reprodutíveis, testes automatizados, métricas de avaliação, demonstrações HTML, APIs locais e interfaces Streamlit.

| Área | IDs | Evidência principal | Acesso |
|---|---|---|---|
| Análise de dados industrial | #001–#010 | Pandas, notebooks e métricas descritivas | [Catálogo](PROJECT_CATALOG.md#01--11--01-dados-análise-de-dados-industrial--industrial-data-analysis) |
| Análise exploratória | #011–#020 | EDA, Pandas, gráficos, SQL | [Casos](site/cases/eda/index.html) |
| Regressão | #021–#030 | Scikit-learn, XGBoost, MAE/R² | [Casos](site/cases/regression/index.html) |
| Classificação | #031–#040 | Treino e separação treino/calibração/teste | [Casos](site/cases/classification/index.html) |
| NLP industrial | #041–#050 | NLP, modelos de texto e avaliação | [Casos](site/cases/nlp/index.html) |
| Recomendação | #051–#060 | Ranking e recomendadores demonstrativos | [Casos](site/cases/recommendation/index.html) |
| Séries temporais | #061–#070 | Backtesting e modelos temporais | [Casos](site/cases/timeseries/index.html) |
| Visão computacional | #071–#080 | OpenCV, OCR e CNNs em imagens artificiais | [Casos](site/cases/vision/index.html) |
| BI e finanças | #081–#090 | SQL SQLite, indicadores e modelos | [Casos](site/cases/business/index.html) |
| Sistemas industriais | #091–#100 | FastAPI, SQLite, Kafka/Redpanda de teste | [Casos](site/cases/advanced/index.html) |
| Motorsport e MLOps | #101–#111 | EKF, simuladores, MLflow, LSTM, Grad-CAM, SHAP; #111 parcial | [Casos](site/cases/motorsport/index.html) |

**Importante:** as tecnologias na tabela se referem às **demonstrações identificadas**, não à utilização de todas elas em cada projeto. Consulte a [matriz individual de evidências](TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv) antes de utilizar os exemplos como comprovação de habilidades.

## Projetos em destaque

- **[#101 — Estratégia de corrida e pit-stops](projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator/)** — simulador de stints e comparação de regressões XGBoost/Random Forest em voltas artificiais.
- **[#104 — Detecção temporal com LSTM](projetos/11-motorsport-f1-mlops/104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline/)** — autoencoder TensorFlow treinado e baseline RMS em sinais fictícios.
- **[#105 — CNN e Grad-CAM](projetos/11-motorsport-f1-mlops/105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam/)** — classificação de radiografias geradas e explicações visuais, não validação NDT real.
- **[#106 — MLOps com MLflow e FastAPI](projetos/11-motorsport-f1-mlops/106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi/)** — tracking local, artefatos recarregáveis e serviço de demonstração.
- **[#109 — Replay de telemetria sintética](projetos/11-motorsport-f1-mlops/109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch/)** — simulação e interface Plotly; não é GPS real nem live timing.
- **[#110 — Engenharia de performance](projetos/11-motorsport-f1-mlops/110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim/)** — física aproximada de pneus, mapa térmico simulado e análise de amortecedores; não usa FLIR nem ChassisSim.

## Reproduzir a auditoria

Requer Python 3.11. Use ambiente virtual e instale dependências conforme o caso escolhido. Evite instalar simultaneamente TensorFlow, PyTorch e MLflow quando não forem necessários.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-integration.txt
python scripts/audit_integrated_portfolio.py --check
python -m unittest discover -s tests -v
```

Para trabalhos mais rápidos, veja [instalação por domínio](docs/GETTING_STARTED.md). Os treinos de CNNs, os testes de Kafka e os pipelines MLOps mais pesados têm workflows específicos.

## Publicação e distribuição

O **GitHub Pages** publica somente a versão estática construída a partir de `site/`; as APIs FastAPI, o Streamlit e os modelos **não rodam dentro do Pages**. O script `scripts/prepare_pages.py` corrige caminhos para `/portfolio/`, gera sitemap, metadados, `.nojekyll` e página 404. Consulte [como publicar](docs/DEPLOYMENT.md).

As **releases** são prévias técnicas versionadas, não lançamentos de software industrial certificado. Após CI verde na `main`, um workflow pode criar a primeira pré-release e publicar contêineres demonstrativos no GitHub Container Registry, de acordo com as permissões disponíveis. Consulte [política de versões](docs/RELEASES.md) e [pacotes e contêineres](docs/PACKAGES.md).

## Qualidade, escopo e governança

O que os testes demonstram: estrutura do catálogo, execução de algoritmos nas fixtures, contratos locais de API/SQL, treinamento sintético e regressões. O que **não** demonstram: eficácia em dados corporativos, operação segura de equipamentos, conformidade regulatória, direitos de uso de telemetria real ou benefícios econômicos observados.

- [Auditoria integrada](INTEGRATION_AUDIT.md) · [Matriz de lacunas por projeto](TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv) · [Roadmap de limitações](QUALITY_ROADMAP.md)
- [Guia de contribuição](CONTRIBUTING.md) · [Política de segurança](SECURITY.md) · [Histórico de versões](CHANGELOG.md)
- [Catálogo completo de 111 projetos](PROJECT_CATALOG.md)

## Contato

**Gabriel Reis Duarte** · [LinkedIn](https://www.linkedin.com/in/gabrielrduarte) · [GitHub](https://github.com/xlDuarte)

Este repositório não publica arquivos de fonte proprietária, credenciais ou dados reais de empresas. **Nenhuma licença de reutilização foi concedida automaticamente**; consulte as condições aplicáveis antes de redistribuir o código.
