# Publicação

## Endereço oficial: Vercel

O site é publicado pela Vercel a partir de `site/`, sem etapa de build no servidor:
**https://gabriel-automotive-industrial-lab.vercel.app**. O arquivo `vercel.json` (gerado por `scripts/build_site.py`) define:

- `cleanUrls` e `trailingSlash`;
- redirecionamentos permanentes das URLs antigas (`/industry/`, `/motorsport/`, `/f1/`, `/about/`…), listados em `scripts/site_data.py`;
- cabeçalhos de segurança (CSP, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`).

`site/` já inclui `404.html`, `sitemap.xml` e `robots.txt`. Cada página tem `canonical` e Open Graph apontando para a Vercel.

## GitHub Pages: só redirecionamento

`scripts/prepare_pages.py` gera em `_site/` um stub por página que redireciona para o mesmo caminho na Vercel (com `canonical`, `noindex`, `meta refresh` e o `#hash` preservado). URLs aposentadas vão direto ao novo destino e a `404.html` encaminha qualquer caminho desconhecido. Assim, links antigos de `xlduarte.github.io/portfolio/` continuam funcionando sem duplicar conteúdo no Google.

```bash
python scripts/prepare_pages.py --repo xlDuarte/portfolio --output _site
python -m unittest discover -s tests -p test_pages_release.py -v
```

---

## Histórico (antes da migração para a Vercel)

# Publicação no GitHub Pages

## URL e arquitetura

Endereço esperado do projeto: **https://xlduarte.github.io/portfolio/**. A publicação efetiva depende do GitHub Pages estar configurado, da visibilidade/permissões da conta e de o job de deploy ter concluído com sucesso.

O repositório é privado; as regras de acesso ao site Pages e os artefatos dependem da configuração do GitHub. Não pressupor que Pages concede acesso público ao código.

O site é gerado **somente** de `site/`; a saída de deploy é `_site/` (temporária, não commitada). `scripts/prepare_pages.py`:
1. Copia sem mutar `site/`.
2. Reescreve URLs raiz relativas de recursos e links locais para `/portfolio/`; com `CNAME` válido usa raiz do domínio personalizado.
3. Insere canonical e Open Graph básicos nas páginas HTML.
4. Gera `sitemap.xml`, `robots.txt`, `.nojekyll` e `404.html`.
5. Mantém arquivos SVG, CSV, JSON e scripts estáticos existentes.

```bash
python scripts/prepare_pages.py --repo xlDuarte/portfolio --output _site
python -m unittest discover -s tests -p test_pages_release.py -v
python -m http.server 8000 --directory _site
```

**Atenção:** o servidor Python acima serve a saída na raiz local (não em `/portfolio/`). Para testar caminhos absolutos de produção, monte a pasta gerada como `<webroot>/portfolio/` no servidor local ou use o GitHub Pages publicado. Se desejar rodar na raiz do servidor, gere com `--base-path ''`.

## Configuração necessária no GitHub

Em **Settings → Pages → Build and deployment**, selecione **GitHub Actions**. Em **Actions → General**, confirme que as políticas de execução permitem os workflows oficiais usados no projeto. O job global `verify` deve terminar com sucesso para liberar `deploy-pages`; o job Pages solicita `pages:write` e `id-token:write`.

O workflow [ci-and-pages.yml](../.github/workflows/ci-and-pages.yml) executa testes, compila o código, prepara `_site` e publica com `actions/deploy-pages`. Se Pages não estiver habilitado, emite aviso e pula a publicação, sem fingir que o site está online.

Verifique em **Actions** se aparecem `deploy-pages` e o endereço publicado. Um status verde em `verify` **não** prova que o deploy ocorreu. Após publicar, teste `/portfolio/`, `/portfolio/cases/business/`, `/portfolio/cases/motorsport/` e `/portfolio/sitemap.xml`.

## URLs / domínio personalizado

Para adicionar domínio, configure DNS e `site/CNAME` com um único hostname válido. O gerador detecta esse arquivo e evita o prefixo do projeto. Não assuma que simplesmente escrever `CNAME` configura automaticamente o DNS ou habilita HTTPS.

## O que não é hospedado

GitHub Pages **não** executa FastAPI, Python, Streamlit, SQL, Kafka, MLflow, Docker ou treinamentos. Links do site representam páginas HTML estáticas e código no GitHub. As APIs só funcionam quando implantadas separadamente com autenticação e infraestrutura adequada.

## Diagnóstico

Se o GitHub devolver 404 de Pages, revise as configurações e rode novamente o workflow. Se as páginas de casos abrirem 404 enquanto a inicial funciona, confira prefixo `/portfolio/` e o build `_site`. Se o domínio personalizado estiver sendo usado, confira o DNS, `CNAME` e propagação TLS.
