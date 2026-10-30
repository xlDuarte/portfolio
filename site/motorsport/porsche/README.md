# Porsche Cup — Performance Lab / projeto 110

Rota canônica: `/cases/motorsport/110/`. O hub redireciona para esta página sem montar o antigo painel. Implementação estática independente, com ECharts 6.0.0 local (`../replay/vendor`) e fallback SVG. Página pessoal, indústria e demais laboratórios permanecem fora do escopo.

## Interface

Identidade inspirada no 911 GT3 Cup: branco, grafite, vermelho, fotografia lateral e logotipo Porsche Motorsport. Estudo independente, com identificação de autoria e referências oficiais. Controles agrupados em cenário de movimento, pneus/contato e chassi/aerodinâmica. Cenários de reta, curva à esquerda e frenagem; seleção de roda; referência congelada para comparação de cargas; exportação JSON com parâmetros, hipóteses, unidades e resultados. A captura 110.webp mostra a interface em funcionamento.

## Modelo e limites

`model.mjs` calcula equilíbrio quase estático. Massa de referência 1260 kg, conforme a página oficial do modelo 992/2021. Os demais parâmetros são hipóteses didáticas: g 9,81; densidade 1,225; área 1,8 m²; CG 0,45 m; bitola 1,6 m; entre-eixos 2,45 m; distribuição dianteira estática 40%, aero 45%, transferência lateral 45%.

A soma de Fz nas quatro rodas é igual ao peso + downforce. Aceleração lateral positiva representa curva à esquerda, carregando as rodas direitas. Aceleração longitudinal negativa representa frenagem, carregando a dianteira. Não há dinâmica transiente de suspensão, cambagem dinâmica, temperatura integrada no tempo ou aquisição real.

Rigidez e três temperaturas por pneu preservam as fórmulas do painel anterior. As novas cargas podem ultrapassar o domínio original de 3067–4972 N; não existe validação dessa extrapolação. A curva saturante de força lateral usa a rigidez como derivada em zero; não é calibração Pacejka de um pneu real. O envelope G-G é uma elipse de capacidade agregada, com escalas visuais iguais nos dois eixos. Não é um modelo completo de aderência combinada por eixo.

A cambagem afeta apenas temperaturas. Pressão afeta temperatura central e rigidez. Carga afeta rigidez, temperaturas e capacidade. Temperatura não retroalimenta a aderência. O ajuste de amortecedor altera apenas uma distribuição sintética normalizada de velocidades da haste. A aerodinâmica é independente do amortecimento, corrigindo o acoplamento artificial anterior. Não executa FLIR, HH Timing nem ChassisSim.

## Validação

`node tests/porsche_checks.mjs`

`python -m unittest discover -s tests -p test_porsche.py`

Testes nos limites: conservação de carga, positividade, simetria, sinais das transferências, dependência quadrática da velocidade no downforce, independência do amortecedor, conservação da distribuição, paridade térmica, derivada de Fy em zero e saturação. Navegador: assets, ECharts, controles, presets, seleção, referência, exportação, restauração, 390/768/1024/1440 px, fallback e rota do hub.

## Créditos e origem dos assets

Referência oficial: https://racing.porsche.com/en-US/cars/911-gt3-cup-2021

- `assets/gt3-cup.webp`: imagem oficial do modelo, obtida do CDN referenciado nessa página, em WebP com limite de 1400 px. Origem: https://res.cloudinary.com/dmwcbhehi/image/upload/v1731403761/Porsche_GT3Cup_Seitenschuss_ro9tv1.png
- `assets/porsche-motorsport.svg`: logotipo vetorial presente no cabeçalho da mesma página oficial; paths e cores preservados.
- Porsche e as respectivas marcas pertencem aos seus titulares. Assets de referência não passam a integrar uma licença de código aberto do projeto. Este estudo não tem vínculo nem endosso da Porsche.

Não são reivindicados tempos de volta oficiais, dados de sensores ou resultados de processo seletivo.
