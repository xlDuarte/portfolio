# Marcas e fotos de terceiros

Registro de origem, licença e crédito de cada imagem ou marca de terceiros usada no site. A fonte de verdade para o build e para os testes é `site/assets/brands/SOURCES.json`; este documento explica as decisões.

| Arquivo | Assunto | Origem | Licença | Crédito | Situação |
|---|---|---|---|---|---|
| `site/assets/photos/911-gt3-cup-{800,1600}.webp` | Porsche 911 GT3 Cup em pista (imagem sintética) | Gerada com o ChatGPT pelo dono do site, 24/11/2026 | Saída de IA do dono do site; marcas da Porsche AG em uso nominativo | "Imagem gerada por IA (ChatGPT)" | Confirmada |
| `site/assets/brands/*.webp` (12 arquivos: F1, Porsche, Red Bull, Ferrari, Mercedes, McLaren, Aston Martin, Alpine, Williams, Haas, Racing Bulls, Sauber) | Marcas da F1, da Porsche e das dez equipes de 2024 | Recriações geradas com o ChatGPT e enviadas pelo dono do site em 24/11/2026. Três arquivos (F1, Racing Bulls, Sauber) trazem manifesto C2PA da OpenAI; os outros nove foram regravados no iPhone, sem manifesto | Saída de IA do dono do site; marcas dos titulares, uso nominativo | "Logotipos recriados por IA (ChatGPT)" | Confirmada |

Os logotipos são coloridos, em WebP com fundo transparente e 128 px de altura. O script `scripts/process_brand_logos.py` reproduz o tratamento a partir dos originais: recorte pela transparência original, margem de 4 %, redimensionamento, sem metadados. Os SVG monocromáticos do `simple-icons` usados antes foram retirados.

### Desvios conhecidos, mantidos por decisão do dono do site

Antes do uso, o dono do site foi avisado destes pontos e decidiu manter todas as imagens.

- **Haas:** o texto do logotipo saiu deformado na recriação (lê-se algo como "HINAS").
- **Racing Bulls:** é a marca de 2025. Nos dados do Bahrein 2024, a equipe se chama RB F1 Team.
- **Sauber:** não é a identidade que a equipe usou em 2024 (Stake F1 Team Kick Sauber).
- Os demais são recriações fiéis na escala em que aparecem (18 a 40 px). Ainda assim, não são os arquivos oficiais.
## Regras

1. Arquivo original da fonte, sem redesenho; só redimensionamento e remoção de metadados. Exceção registrada: os logotipos atuais são recriações por IA escolhidas pelo dono do site, e todas as páginas que os mostram dizem isso.
2. Uso nominativo: identifica a categoria estudada; nunca como marca do site.
3. Toda página que usa imagem ou marca de terceiros mostra o aviso "Projeto independente, sem vínculo…" e, quando confirmado, o crédito (o teste `test_every_third_party_image_has_provenance` confere).
4. Material do Porsche Newsroom é destinado a jornalistas e não a uso comercial ou promocional; usar só com autorização escrita.

5. Imagem gerada por IA é identificada como tal na legenda e no texto alternativo, para não passar por fotografia. Logotipo recriado por IA é identificado no aviso de marcas da página.
