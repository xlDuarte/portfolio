# Marcas e fotos de terceiros

Registro de origem, licença e crédito de cada imagem ou marca de terceiros usada no site. A fonte de verdade para o build e para os testes é `site/assets/brands/SOURCES.json`; este documento explica as decisões.

| Arquivo | Assunto | Origem | Licença | Crédito | Situação |
|---|---|---|---|---|---|
| `site/assets/photos/911-gt3-cup-{800,1600}.webp` | Porsche 911 GT3 Cup em pista (imagem sintética) | Gerada com o ChatGPT pelo dono do site, 24/11/2026 | Saída de IA do dono do site; marcas da Porsche AG em uso nominativo | "Imagem gerada por IA (ChatGPT)" | Confirmada |
| `site/assets/brands/{formula-1,porsche,red-bull,ferrari,mclaren,aston-martin}.svg` | Marcas F1, Porsche e equipes | Pacote npm `simple-icons` 16.38.1 (fonte declarada por ícone no `SOURCES.json`) | Desenho do ícone CC0-1.0; marcas dos titulares, uso nominativo | "Marcas pertencem aos seus titulares" | Confirmada |

Logos monocromáticos (uma cor oficial), vetoriais. Faltam Mercedes, Alpine, Williams, Haas, Racing Bulls e Sauber: o pacote não os inclui e o ambiente de build não alcança os sites das equipes. Enquanto isso, essas equipes aparecem só pelo nome.

## Regras

1. Arquivo original da fonte, sem redesenho; só redimensionamento e remoção de metadados.
2. Uso nominativo: identifica a categoria estudada; nunca como marca do site.
3. Toda página que usa imagem ou marca de terceiros mostra o aviso "Projeto independente, sem vínculo…" e, quando confirmado, o crédito (o teste `test_every_third_party_image_has_provenance` confere).
4. Material do Porsche Newsroom é destinado a jornalistas e não a uso comercial ou promocional; usar só com autorização escrita.

5. Imagem gerada por IA é identificada como tal na legenda e no texto alternativo, para não passar por fotografia.
