# Gabriel Reis Duarte — portfólio de dados e engenharia

Dados, software e engenharia aplicados a dois nichos: **operação industrial** e **automobilismo de desempenho** (Fórmula 1 e Porsche Cup).

**Site:** [gabriel-automotive-industrial-lab.vercel.app](https://gabriel-automotive-industrial-lab.vercel.app) · [LinkedIn](https://www.linkedin.com/in/gabrielrduarte) · [Como executar](docs/GETTING_STARTED.md)

[![CI](https://github.com/xlDuarte/portfolio/actions/workflows/ci-and-pages.yml/badge.svg?branch=main)](https://github.com/xlDuarte/portfolio/actions/workflows/ci-and-pages.yml)

## Como o portfólio está organizado

| Seção | O que tem | Dados |
|---|---|---|
| [Industrial](https://gabriel-automotive-industrial-lab.vercel.app/industrial/) | 5 estudos de caso completos (OEE ponderado, OTIF, CAPEX, previsão de demanda, churn) e um catálogo de 100 exercícios técnicos por técnica (#001–#100) | Sintéticos, com semente fixa |
| [Automotivo › Fórmula 1](https://gabriel-automotive-industrial-lab.vercel.app/automotivo/f1/) | Modelos e probabilidades de corrida, estratégia de pneus, telemetria com filtro de Kalman, replay, direção de prova e laboratórios de aerodinâmica, energia e tempo de volta | **Reais e públicos** (OpenF1, FastF1, Jolpica) |
| [Automotivo › Porsche Cup](https://gabriel-automotive-industrial-lab.vercel.app/automotivo/porsche/) | Laboratório de engenharia: carga por roda, temperatura de pneus, dinâmica veicular | Aquisição importada pelo usuário |
| [Laboratório comum](https://gabriel-automotive-industrial-lab.vercel.app/laboratorio/) | Visão computacional, vibração (LSTM), inspeção radiográfica (CNN + Grad-CAM), MLOps (MLflow + FastAPI), explicabilidade (SHAP) — técnicas que servem aos dois nichos | Sintéticos ou importados |

## Por onde começar

- **Industrial:** [OEE ponderado](https://gabriel-automotive-industrial-lab.vercel.app/cases/oee/) e [OTIF e ruptura](https://gabriel-automotive-industrial-lab.vercel.app/cases/supply/) — código em [`case_studies/`](case_studies/).
- **Fórmula 1:** [modelos e probabilidades](https://gabriel-automotive-industrial-lab.vercel.app/motorsport/f1-pip/) — treino em [`scripts/train_f1_real.py`](scripts/train_f1_real.py), oito modelos com validação temporal.
- **Porsche Cup:** [laboratório de engenharia](https://gabriel-automotive-industrial-lab.vercel.app/cases/motorsport/110/) — código em [`site/motorsport/porsche/`](site/motorsport/porsche/).

## Transparência

- Projetos industriais usam bases **sintéticas** porque dados de fábrica são confidenciais. Nenhum projeto usa dado de empresa onde o autor trabalhou.
- Os 100 projetos do catálogo industrial são **exercícios curtos**: rodam de verdade e têm teste, mas compartilham um motor de cálculo por técnica. Os estudos de caso e os projetos de F1 são os trabalhos mais profundos.
- Os testes provam que o código faz o que diz; **não** provam desempenho em dados corporativos, operação segura de equipamentos ou ganho financeiro. A [matriz de evidências](TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv) separa, projeto a projeto, o que foi feito do que não foi.
- Projeto independente, sem vínculo com Fórmula 1, FIA, Porsche ou equipes.

## Executar localmente

Requer Python 3.11. Instale só o domínio que for usar ([lista de dependências](requirements/)).

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements/integration.txt
python scripts/audit_integrated_portfolio.py --check
python -m unittest discover -s tests -v
```

O site é estático e fica em [`site/`](site/). Depois de alterar páginas ou dados, regenere:

```bash
python -m pip install -r requirements/site.txt
python scripts/build_site.py        # hubs, páginas de projeto, sitemap, vercel.json
```

O CI falha se `site/` não corresponder ao resultado do build.

## Estrutura

```
site/                 site estático publicado na Vercel (design system em site/assets/ds.css)
scripts/              build do site (build_site.py, site_data.py), auditoria, treino F1
projetos/             111 pontos de entrada numerados (#001–#111), um README cada
*_batch/              motores de cálculo por técnica (regressão, NLP, visão, BI…)
case_studies/         estudos de caso industriais completos
f1-predictive-intelligence/   pipeline de treino walk-forward do projeto #111
tests/                suíte automatizada (Python + Node)
docs/                 guias e relatórios históricos de auditoria (docs/reports/)
```

## Publicação

A Vercel publica `site/` como endereço oficial (`vercel.json` define redirecionamentos das URLs antigas e cabeçalhos de segurança). O GitHub Pages continua ativo apenas para redirecionar links antigos para a Vercel — veja [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Qualidade e governança

[Auditoria integrada](INTEGRATION_AUDIT.md) · [Roadmap de limitações](QUALITY_ROADMAP.md) · [Catálogo dos 111 projetos](PROJECT_CATALOG.md) · [Contribuição](CONTRIBUTING.md) · [Segurança](SECURITY.md) · [Histórico](CHANGELOG.md)

## Licença

Código sob [licença MIT](LICENSE). A fonte Archivo é distribuída sob a [SIL Open Font License](site/assets/fonts/OFL.txt). Fotos do autor não estão incluídas na licença MIT.
