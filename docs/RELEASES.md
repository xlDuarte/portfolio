# Política de releases e versionamento

O repositório contém **111 estudos**, não um produto industrial único com SLA. Releases documentam fotografias verificáveis do código e das demonstrações; não indicam que todos os projetos cumprem os escopos anunciados.

## Prévia inicial

`v0.1.0-preview.1` — pré-release (não estável), com matriz técnica, `portfolio-pages-preview.zip` e código-fonte apontando para um commit exato de `main`. Consulte [notas](releases/v0.1.0-preview.1.md).

## Automação

O workflow [preview-release-ghcr.yml](../.github/workflows/preview-release-ghcr.yml) é disparado ao concluir **com sucesso** o workflow global `Integrated portfolio - 111 projects quality gates and Pages` da `main`. Ele verifica que o commit avaliado ainda é o `main` atual; caso contrário, pula o lançamento.

Se a tag **não** existir, cria automaticamente uma pré-release com ZIP do site e CSV da matriz técnica. Se a tag existir, **não altera retroativamente a release** nem republica o mesmo número para outro commit. O mesmo workflow aceita execução manual (*Actions → Preview release and GHCR demo packages → Run workflow*) com nova tag SemVer, para versões futuras, sempre após validação.

A publicação da release exige permissão `contents:write`. Se o repositório/política do GitHub impedir criação de releases, o job falhará de modo explícito; nenhuma release deve ser considerada criada até aparecer em **Releases**.

## Artefatos e pacotes

- **Release ZIP:** saída HTML estática, com URL para Pages corrigida; não inclui serviços Python rodando no Pages.
- **CSV de evidências:** funcionalidades e lacunas documentadas por projeto.
- **Packages GHCR:** imagens de API experimentais, publicadas apenas após criação da release e conforme permissão `packages:write`. O status de release **não garante** que o job de contêiner terminou verde.

Consulte [pacotes](PACKAGES.md).

## Critérios antes de v1.0.0

- Modelos realmente treinados, avaliados e versionados para o catálogo #111.
- Critérios de aceite, dados e métricas reais/licenciados por projeto, com proveniência.
- Sem atribuição incorreta de ferramentas no README.
- Controles de segurança/autenticação para as aplicações que precisarem de implantação.
- DAX executado e testado num mecanismo Power BI/Tabular, quando anunciado.
- Revisão e documentação de licenciamento, direitos autorais, restrições de uso e privacidade.
