# Direção de arte: "Telemetria viva"

Fase 0 do plano de redesenho visual (`claude/PROMPT-PORTFOLIO-VISUAL-SURREAL.md`, no Projeto). Este documento fixa a linguagem visual antes de qualquer página nova. O protótipo do herói da home está em `/prototipos/heroi/` e segue tudo o que está aqui.

## 1. Brief fixado

A direção foi definida no prompt aprovado pelo dono do site, com mundo e primeira tela nomeados. Por isso não houve rodada de alternativas.

| Campo | Decisão |
|---|---|
| Mundo | Instrumento de medição em funcionamento: os dados do próprio repositório viram matéria visual |
| Primeira tela | Duas maquetes que se tocam no centro: linha de produção isométrica (OEE) e Sakhir em 3D (OpenF1) |
| Modo | Experiência (portfólio): o trabalho conduz a primeira tela, a interface recua |
| Mantido | Fundo claro, Archivo auto-hospedada, tokens de `ds.css`, cobalto e vermelho como sinalização |
| Público | Recrutadores e gestores de engenharia, motorsport e indústria, em desktop no escritório e no celular |

## 2. Diagnóstico do estado atual

Antes (home publicada): título grande, retrato e dois cartões de nicho com listas. Arquitetura correta, mas visualmente igual a qualquer portfólio limpo.

| Problema | Efeito | Resposta da nova direção |
|---|---|---|
| Nenhuma imagem do trabalho na primeira tela | O visitante lê sobre dados, mas não vê dado nenhum | A primeira tela é feita dos próprios dados |
| Os dois nichos são cartões iguais | A diferença entre indústria e pista fica só na cor | Cada nicho ganha material e movimento próprios |
| Números aparecem só no texto | "77,5% de OEE" não se sente | O OEE move a esteira; a velocidade real colore a pista |
| O Laboratório comum é uma faixa solta | Parece rodapé, não ponte | Vira o marco que fica sobre a junção das duas maquetes |

## 3. Princípios

1. **Nada é decoração.** Todo movimento lê um arquivo do repositório. Se um valor é escala de exibição (relevo exagerado, carro aumentado), isso fica escrito no código e na legenda.
2. **Maquete, não videogame.** Objetos sobre bases, luz de estúdio, sombras suaves. Lembra modelo técnico em vitrine, não cena de jogo.
3. **Um momento autoral por página.** A abertura (o nome abre como um mostrador e as maquetes assentam) é o único movimento sem gatilho. O resto responde ao visitante.
4. **Cor de nicho sinaliza, nunca enfeita.** Cobalto e vermelho aparecem onde há escolha de caminho ou dado.
5. **Honestidade visível.** Cada maquete diz se o dado é real (OpenF1) ou sintético (semente fixa).

## 4. Paleta estendida

Base (já existente em `ds.css`, não muda):

| Token | Hex | Uso |
|---|---|---|
| `--paper` | `#ffffff` | Fundo |
| `--wash` | `#f4f6f8` | Fundo do palco 3D, áreas de apoio |
| `--rule` / `--rule-strong` | `#e3e6ea` / `#c9ced5` | Divisões |
| `--graphite` | `#1c2128` | Texto, junção das maquetes, Laboratório |
| `--slate` | `#59616b` | Texto secundário (contraste 6,3:1 sobre branco) |
| `--ind` / `--ind-wash` | `#1d4e9e` / `#eef3fb` | Industrial |
| `--auto` / `--auto-wash` | `#b8122b` / `#fbeff1` | Automotivo |
| `--lab` | `#3b4652` | Laboratório comum |

Materiais 3D (só na cena, nunca em texto):

| Nome | Hex | Onde |
|---|---|---|
| Aço escovado | `#cfd5dc` (metalness 0,75, roughness 0,32) | Máquinas |
| Aço escuro | `#9aa3ad` | Estruturas, pés da esteira |
| Esteira | `#3a4048` | Superfície da esteira, com taliscas |
| Concreto | `#eceff2` | Piso da fábrica |
| Faixa de piso | `#d9dee4` | Marcação de corredor |
| Asfalto | `#2f343b` | Superfície da pista |
| Resina | `#c9cfd6` | Paredes da maquete da pista (altura = relevo real × 4) |
| Base de maquete | `#f7f8fa` | Pedestal sob a pista |

Cores de dado (gráficos e cena, nunca texto):

| Nome | Hex | Significado |
|---|---|---|
| Rampa de velocidade | `#eceef1` → `#ff3048` | Velocidade de Verstappen na volta de referência (65 a 296 km/h, amostras de 4 Hz) |
| Em operação | `#1b7a48` | Linha rodando |
| Parada | `#c58a00` (texto: `#8a5a00`) | Linha parada por disponibilidade |
| Refugo | `#b8122b` | Peça reprovada e caçamba |
| Setor roxo / verde / amarelo | `#7b2fbe` / `#1f9d55` / `#d9a300` | Convenção de cronometragem da F1, para as páginas de F1 |

## 5. Tipografia

Uma família só: Archivo variável (peso 100–900, largura 62–125%). A largura é a voz da marca: condensada lembra mostrador e ficha técnica; larga lembra título de pôster.

| Nível | Tamanho | Largura | Peso | Uso |
|---|---|---|---|---|
| Nome no herói | `clamp(3rem, 9vw, 6rem)` | 62% → 112% na abertura; 112% → 70% ao rolar | 780 | Só na home |
| h1 de página | `--step-5` | 78% | 760 | Hubs e estudos |
| h2 | `--step-3` | 82–85% | 700 | Seções, legendas das maquetes |
| h3 | `--step-1` | 95% | 650 | Subseções |
| Corpo | `--step-0` (17px) | 100% | 400 | Texto, até 68 caracteres por linha |
| Leitura de dado | `--step--1` | 100% | 400/650 | Tabelas e mostradores, sempre `tabular-nums` |

Regras: rastreamento entre -0,02 e -0,025em em títulos; sem caixa alta em rótulos; sem fonte monoespaçada como fantasia (números usam algarismos tabulares da própria Archivo).

## 6. Movimento

| Tipo | Duração | Curva | Exemplo |
|---|---|---|---|
| Microinteração | 120–200 ms | `ease` | Botão, link |
| Mudança de estado | 300–450 ms | `cubic-bezier(.16,1,.3,1)` | Fundo do nicho ao passar o mouse, traço sob o título |
| Câmera e divisão | constante de 7/s (amortecimento exponencial) | — | A maquete escolhida cresce para 62% |
| Abertura | 1,6–2,2 s | `expo.out` (GSAP) | Nome abre, câmeras assentam, legendas sobem 14 px |
| Tempo de dado | 1× real | linear | Replay de Sakhir em tempo real; uma órbita a cada 4 min |

`prefers-reduced-motion`: sem abertura, sem órbita, sem replay; um quadro estático representativo e o nome em largura fixa. Sem WebGL: desenho vetorial gerado dos mesmos dados (`hero-fallback.svg`).

## 7. Materialidade por nicho

- **Industrial:** aço escovado, piso de concreto com faixas de corredor, vista isométrica ortográfica. A esteira para pela disponibilidade (89,4%), corre pelo desempenho (90,1%) e desvia peças reprovadas para a caçamba pela qualidade (96,3%).
- **Fórmula 1:** asfalto escuro sobre paredes de resina, como maquete fresada; relevo de Sakhir exagerado quatro vezes; linha de corrida colorida pela velocidade real; rastro de 6 s atrás de cada carro.
- **Porsche Cup (Fase 2):** prata da pintura do GT3 Cup, borracha, diagrama de quatro rodas com carga por roda. Modelo 3D só com licença válida (ver seção 7 do prompt).
- **Laboratório comum:** grafite, nuvem de pontos que muda de forma (onda de vibração, peça em raio-X, fluxo óptico).

## 8. Wireframes

Home (protótipo pronto):

```
┌────────────────────────────────────────────────────────────┐
│ Gabriel Reis Duarte                 Industrial Automotivo… │
│                                                            │
│ Gabriel Reis Duarte  (largura variável, abre como mostrador)│
│ Dados, software e engenharia para dois nichos…             │
├──────────────────────────────┬─────────────────────────────┤
│ [OEE 77,5% · linhas A/B]     │                             │
│      linha isométrica        │    Sakhir 3D, 3 carros       │
│      (esteira = OEE)         │    (cor = velocidade)        │
│                              │        [VER 284 km/h 7ª]    │
├──────────── [ Laboratório comum ] ─────────────────────────┤
│ Industrial                   │ Automotivo de desempenho    │
│ dados sintéticos · tabela    │ dados reais · legenda       │
└──────────────────────────────┴─────────────────────────────┘
  hover/foco num lado: ele cresce para 62%, fundo ganha a cor do nicho
  celular: maquetes empilhadas, legendas abaixo
```

Industrial:

```
┌────────────────────────────────────────────────────────────┐
│ Industrial (h1)          resumo em 2 linhas                │
│ ┌─ gêmeo digital isométrico: 5 máquinas = 5 estudos ─────┐ │
│ │  [OEE] [OTIF] [CAPEX] [Previsão] [Churn]  clique → zoom │ │
│ └─────────────────────────────────────────────────────────┘ │
│ Painel dos 100 projetos: filtro por técnica │ contagem viva │
│ linhas com métrica real de cada metrics.json               │
└────────────────────────────────────────────────────────────┘
```

Automotivo (hub):

```
┌───────────────────────────┬────────────────────────────────┐
│  Garagem F1               │  Garagem Porsche Cup           │
│  porta abre no hover →    │  porta abre no hover →         │
│  pista em miniatura       │  carro em plataforma giratória │
├───────────────────────────┴────────────────────────────────┤
│ Projetos compartilhados → Laboratório comum                │
└────────────────────────────────────────────────────────────┘
```

Fórmula 1:

```
┌────────────────────────────────────────────────────────────┐
│ Sakhir 3D em largura total, replay contínuo, câmera orbital │
│ mostrador lateral: volta, velocidade, marcha, DRS          │
├────────────────────────────────────────────────────────────┤
│ Muro do pit: 5 ferramentas como estações (cartão + estado)  │
│ Grade de modelos com logos das equipes (fase de marcas)     │
│ Projetos #101 #102 #107 #109                                │
└────────────────────────────────────────────────────────────┘
```

Porsche Cup:

```
┌────────────────────────────────────────────────────────────┐
│ GT3 Cup em 3D (ou foto autorizada), giratório               │
│ 4 rodas acendem pela carga simulada; calor nos pneus        │
├────────────────────────────────────────────────────────────┤
│ Módulos do laboratório como painéis de engenharia (#110)    │
└────────────────────────────────────────────────────────────┘
```

Laboratório comum e Sobre:

```
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ nuvem de pontos que vira:    │ │ linha do tempo arrastável    │
│ onda → peça → fluxo óptico   │ │ Direito → ADS → dados → CC   │
│ 5 projetos, cada um ligado   │ │ foto em tratamento editorial │
│ aos dois nichos              │ │                              │
└──────────────────────────────┘ └──────────────────────────────┘
```

Estudo de caso:

```
┌────────────────────────────────────────────────────────────┐
│ Resumo executivo (3 linhas)                                 │
│ rolagem fixada: problema → dado → método → resultado →      │
│ limitação; o gráfico ao lado muda a cada etapa              │
│ números contam a partir de metrics.json                     │
└────────────────────────────────────────────────────────────┘
```

## 9. Referências e o que emprestar

| Site | Reconhecimento | O que emprestar | O que não emprestar |
|---|---|---|---|
| Lusion v3 (lusion.co) | Site do Ano e Site do Ano para Desenvolvedores, Awwwards 2023 | Interface limpa convivendo com 3D intenso, sem fontes extravagantes nem cores berrantes | Efeitos sem ligação com conteúdo |
| Igloo Inc (igloo.inc) | Site do Ano, Awwwards 2024 | 3D imersivo com navegação por rolagem fácil; a rolagem conta a história | Fundo escuro e clima de jogo |
| Stripe BFCM | Site do Dia, Awwwards (jan/2025) | Uma "máquina" que mostra números reais do negócio em tempo real | Escala de microsite de campanha |

## 10. O que foi cortado por ser clichê

- Número gigante com rótulo pequeno como herói (o modelo padrão de "métrica").
- Rótulo em caixa alta acima de cada título; numeração 01/02/03 sem sequência real.
- Monoespaçada para parecer técnico; brilho neon; fundo escuro com um único verde-ácido.
- Revelação "sobe e aparece" em toda seção.
- Logo de equipe ou da Porsche como identidade do site.

## 11. Desempenho medido no protótipo

| Item | Valor | Meta |
|---|---|---|
| Dados do herói (`hero-data.json`) | 134 KB, 49 KB gzip (Fase 1, com cinemática) | ≤ 2,5 MB por cena |
| Módulo 3D (Three.js 0.187 + GSAP 3.15 + motor de cena, minificado) | 198 KB gzip (Fase 1) | Carregado só depois do `load`, em tempo ocioso |
| Primeiro conteúdo | HTML + CSS + SVG estático; nenhum JS no caminho crítico | LCP < 2,5 s |
| Pausa | Fora da tela (IntersectionObserver) e com a aba oculta | — |
| Resolução | DPR limitado a 2 | — |

Lighthouse em celular real fica para a Fase 5; o ambiente desta fase só roda WebGL por software.

## 12. Pendências

1. Aprovação desta direção e do protótipo antes da Fase 1.
2. Foto do GT3 Cup: escolher (a) foto própria, (b) Creative Commons ou (c) autorização escrita da Porsche.
3. Fase 1 decide se o empacotamento fica no esbuild (hoje) ou passa para Vite.

## 13. Fase 1: motor de cena, física e efeitos

**Motor (`frontend/scene/engine.js`).** Uma tela, várias cenas. Cada vista renderiza num buffer do tamanho da sua maior largura possível e a composição mostra um recorte central, então a divisão animada "varre" entre as cenas sem realocar buffers. Três níveis de qualidade, escolhidos pelo aparelho e rebaixados sozinhos se o quadro passar de ~26 ms por 1,5 s:

| Nível | Pós-processamento | DPR máx. |
|---|---|---|
| alta | GTAO (oclusão ambiente) + bloom HDR + MSAA 4× + vinheta e grão | 2 |
| média | bloom HDR + vinheta e grão | 1,5 |
| baixa | render direto | 1 |

`?q=0|1|2` força um nível (para testes). Mapeamento de tons Khronos PBR Neutral, que preserva as cores de material e o fundo claro.

**Física (`frontend/scene/physics.js`, testada em `physics.test.mjs`).**

| Elemento | Modelo | Parâmetros declarados |
|---|---|---|
| Faíscas de solda | Balística com arrasto quadrático implícito; convecção newtoniana + radiação (Stefan–Boltzmann); quique com restituição e atrito de Coulomb | Gota de aço de 0,2 mm: k = 0,27 1/m, h = 3,9 1/s, ε = 0,8, e = 0,38, μ = 0,45 |
| Cor das faíscas e dos discos | Lei de Planck integrada nas funções CIE 1931 (ajuste de Wyman, Sloan e Shirley, 2013) → sRGB linear; intensidade ∝ T⁴ | Tabela de 500 a 4000 K |
| Peças reprovadas | Corpo rígido por impulsos: restituição na normal, atrito de Coulomb na tangente, giro pelo deslizamento; passo fixo de 240 Hz | e = 0,22, μ = 0,6, cubo de 0,21 m |
| Carros | Arfagem e rolagem por massa-mola-amortecedor de 2ª ordem alimentado pelas acelerações derivadas | 2,2 Hz / ζ 0,65 (arfagem), 2,6 Hz / ζ 0,7 (rolagem); exagero de 1,2°/g e 1,0°/g |
| Faíscas de titânio | Mesmo integrador, partícula mais quente e de resfriamento lento (combustão) | Gatilho ilustrativo: acelerador > 97% e > 265 km/h |

**Cinemática em Python (`scripts/telemetry_physics.py`, testada em `tests/test_telemetry_physics.py`).** Savitzky–Golay sobre relógio uniforme de 4 Hz: a_long = dv/dt pelo canal de velocidade; a_lat = v·dψ/dt pelo rumo da trajetória suavizada. A amostragem pública (~3,7 Hz) atenua picos: a frenagem aparece entre −2,8 e −3,9 g, onde registradores de bordo mostrariam cerca de −5 g. Temperatura do disco dianteiro por modelo de massa térmica única integrado com RK4 (convecção forçada + radiação, potência de frenagem descontado o arrasto); resultado entre ~280 e ~810 °C no trecho, faixa plausível, mas é estimativa.
