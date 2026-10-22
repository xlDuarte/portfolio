# Packages / GitHub Container Registry

## O que é publicado

Duas imagens de **demonstração, não produção**, são definidas no workflow [preview-release-ghcr.yml](../.github/workflows/preview-release-ghcr.yml) e construídas após uma pré-release aprovada:

| Pacote OCI esperado | Dockerfile | Execução |
|---|---|---|
| `ghcr.io/xlduarte/industrial-analytics-api-demo:v0.1.0-preview.1` | `advanced_batch/Dockerfile` | FastAPI com eventos e dados fictícios, SQLite local |
| `ghcr.io/xlduarte/motorsport-mlops-api-demo:v0.1.0-preview.1` | `motorsport_batch/Dockerfile` | Servidor FastAPI de inferência; requer modelo MLflow fornecido separadamente |

**A existência destas referências na documentação não significa que os packages já foram criados.** Confira [GitHub Packages](https://github.com/xlDuarte?tab=packages) e a execução do job `ghcr-demo-packages`. Como o repositório é privado, os pacotes podem ser privados por padrão, e a mudança de visibilidade/regras depende de configurações autorizadas no GitHub.

## Uso local após publicação e autorização

```bash
# Se o pacote for privado: gh auth login; gh auth token | docker login ghcr.io -u xlduarte --password-stdin
docker pull ghcr.io/xlduarte/industrial-analytics-api-demo:v0.1.0-preview.1
docker run --rm --name industrial-api -p 127.0.0.1:8000:8000 \
  ghcr.io/xlduarte/industrial-analytics-api-demo:v0.1.0-preview.1
# GET http://127.0.0.1:8000/health
```

O contêiner de MLOps inclui serviço e dependências, **não** os pesos do modelo treinado. Seu endpoint de predição pode responder 503 até ser configurado um `MLOPS_MODEL_URI` válido e um MLflow Tracking Store apropriado. Não exponha nenhuma das APIs à internet sem revisar autenticação, TLS, permissões, armazenamento, logs, privacidade, autenticação do modelo e rate limiting.

## Ambiente de desenvolvimento sem GHCR

```bash
docker build -f advanced_batch/Dockerfile -t industrial-api-demo:local .
docker run --rm -p 127.0.0.1:8000:8000 industrial-api-demo:local
```

Não inclua senhas, dados sensíveis ou registros corporativos nas imagens. `Dockerfile` e CI **não certificam segurança em produção**.
