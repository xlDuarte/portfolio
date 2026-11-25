# Datasets externos: Hugging Face Hub

Como o portfólio traz dados reais do Hugging Face Hub sem perder a rastreabilidade das fases anteriores (ONS, INMET, CWRU, C-MAPSS, ZeMA).

## Como funciona

| Etapa | Onde roda | O que garante |
|---|---|---|
| Descoberta | Conector do Hugging Face no Claude (busca, cartão, licença, estrutura) | Licença e origem lidas no cartão antes de qualquer download |
| Manifesto | `data/hf/<nome>.json` | Repositório, licença, se pode ser redistribuído, citação da fonte original, projetos que usam e os arquivos (padrões glob) |
| Fixação | `python scripts/fetch_hf.py pin <nome>` no GitHub Actions | Commit do Hub (SHA de 40 caracteres) e um SHA-256 da lista de arquivos nesse commit |
| Download | `python scripts/fetch_hf.py fetch <nome>` | Cada arquivo conferido pelo SHA-256 (LFS/Xet) ou pelo id de blob git; o que falha é descartado |
| Uso | `data/external/hf/<nome>/` (ignorado pelo git) | Dados com `redistribute: false` nunca entram no repositório; o site publica só resultados derivados, com citação |

O ambiente onde o Claude trabalha não alcança `huggingface.co`; os runners do GitHub alcançam. Por isso a fixação e o download rodam no workflow [`datasets-hf.yml`](../.github/workflows/datasets-hf.yml):

- em PR ou push que mexe num manifesto: testes offline, fixação dos manifestos novos, confronto dos já fixados com o Hub e download de três arquivos de cada; os manifestos atualizados ficam num artefato para o commit da fixação;
- manualmente (aba Actions → "Hugging Face datasets" → Run workflow → nome do manifesto): download completo e verificado, como artefato que expira em um dia, para desenvolvimento.

Datasets públicos não precisam de token. Para datasets com acesso restrito, cadastre um token de leitura como segredo do repositório `HF_TOKEN`; o script lê só a variável de ambiente, envia o token apenas a `huggingface.co` (nunca ao redirecionamento de armazenamento) e nunca o imprime. O segredo não é usado em pull requests.

## Catálogo inicial (fase 6, materiais e visão)

| Manifesto | Repositório no Hub | Projetos | Licença | Situação |
|---|---|---|---|---|
| `gc10-det` | [imaadd05/gc10-det](https://huggingface.co/datasets/imaadd05/gc10-det) | #076, #073 | CC BY 4.0 pela Roboflow; original sem licença declarada | Baixar no build, não versionar |
| `mvtec-ad` | [foersben/mvtec-ad](https://huggingface.co/datasets/foersben/mvtec-ad) (metal_nut e screw) | #076, #104 | CC BY-NC-SA 4.0 | Uso não comercial; não versionar |
| `gtsrb` | [tanganke/gtsrb](https://huggingface.co/datasets/tanganke/gtsrb) | #077 | Não declarada no cartão | Conferir os termos do INI antes de publicar imagens; só métricas agregadas até lá |

O cartão do `tanganke/gtsrb` declara 26.640 imagens de treino, menos que as 39.209 do treino oficial do GTSRB; a divisão precisa ser conferida antes de comparar com resultados publicados.

**Avaliados e não adotados**

| Repositório | Motivo |
|---|---|
| `Voxel51/severstal_steel_defects` | Dados de competição do Kaggle (Severstal); o cartão não declara licença e os termos da competição restringem redistribuição |
| `Zhaosxian/SteelDefectX` e cópias | Sem cartão (README de 30 bytes) e sem origem declarada, apesar da etiqueta CC BY 4.0 |
| `ybli/yolo-neu-det-*` | O repositório só aponta para um site externo de download |
| Microestrutura metalográfica (#080) | Nenhum conjunto com origem e licença claras no Hub; o UHCS (NIST/CMU) segue como alvo, por outra via |

## Adicionar um dataset

1. Ler o cartão no Hub: licença, origem, citação, divisão treino/teste e contagens.
2. Criar `data/hf/<nome>.json` com `repo_id`, `title`, `projects`, `license`, `license_note`, `redistribute`, `source.citation` e `include`.
3. Abrir PR: o workflow fixa o commit e confere o download. Baixar o artefato `hf-manifests` e commitar o manifesto fixado.
4. No código do projeto, ler de `data/external/hf/<nome>/`, conferir as contagens do cartão e citar a fonte na página.
