# Modelos F1 — Intelligence Lab

Página canônica: `/f1-models/`. O redesign mantém a rota existente e o relatório `evaluation.json` intacto. Não altera o hub F1-PIP, os demais laboratórios, a página principal ou a página industrial.

## Funcionalidades

Probabilidades de vitória, pódio e top 10 por piloto fictício; comparação de distribuições de chegada entre dois pilotos; matriz piloto × posição; posição média, quantis P10/P50/P90 e erro-padrão Monte Carlo; comparação dos oito modelos por MAE e log-loss; inspeção das métricas arquivadas. Simulações de 500, 3000 ou 10000 corridas, temperatura de 0,5 a 8, semente de 1 a 999999. Alterações no formulário só são aplicadas com “Simular cenário”; a exportação usa sempre os parâmetros da última execução e informa alterações pendentes.

Os temas das 11 equipes de 2026 alteram apenas a aparência. Não atribuem os resultados sintéticos a equipes ou pilotos reais. F1, Mercedes, Ferrari, Red Bull Racing, McLaren, Racing Bulls, Alpine, Haas, Audi, Williams, Aston Martin e Cadillac estão representados com assets locais e créditos.

## Dados e métodos

`model.mjs` expande o algoritmo Plackett–Luce de `../lab/engine.mjs`, preservando a ordem de amostragem e o gerador pseudoaleatório. Para semente 111, as probabilidades de vitória/pódio e posições médias são idênticas ao motor anterior. Agora todas as posições de todas as corridas são contadas, permitindo histogramas e quantis sem aproximá-los por uma distribuição paramétrica.

O relatório contém métricas dos oito modelos, mas escores por piloto apenas do modelo selecionado Ridge. A seleção no comparador inspeciona métricas, sem inventar previsões de modelos não exportados. Os resultados arquivados podem diferir da reamostragem no navegador. Não ocorre treinamento no cliente.

As métricas foram utilizadas na seleção de modelo e ajuste de temperatura. Não representam teste independente. Pilotos D00–D11, equipes T00–T05 e eventos são sintéticos. Não há abandonos, empates, calibração externa ou relação entre o tema de equipes e o modelo. O erro-padrão é de amostragem Monte Carlo, não incerteza de generalização. A temperatura controla a dispersão do ranking; não é temperatura física.

## Visualização e resiliência

ECharts 6.0.0 servido de `../replay/vendor`, com licenças já versionadas. Quatro gráficos com seleção e tooltips. SVG mantém os gráficos disponíveis se a biblioteca falhar. Tabelas numéricas recolhíveis, controles rotulados e tratamento explícito de falha do relatório. A captura de funcionamento é `../lab/screenshots/111.webp`.

## Verificação

`node tests/f1_models_checks.mjs`

`python -m unittest discover -s tests -p test_f1_models_ui.py`

Cobertura numérica: paridade com o motor anterior nos limites de temperatura e número de simulações; somas de probabilidades; uma posição por piloto por corrida; um piloto por posição; quantis ordenados; determinismo; mudança de semente; vencedores por métrica; 11 temas distintos.

Validação no navegador: logotipo F1 e 11 equipes, isolamento dos temas, seleção de pilotos, comparação, métricas, parâmetros, simulação, exportação, responsividade, fallback SVG e falha de carregamento dos dados.

## Assets e referências

Lista oficial: https://www.formula1.com/en/teams (consultada em 29/10/2026).

`assets/sources.json` registra URLs originais dos logotipos encontrados na página oficial. Os logotipos das equipes foram obtidos do CDN Formula 1 em WebP com largura 128 px; o logotipo F1 é SVG. Cores de interface são referências visuais ajustadas para leitura, não especificações oficiais de marca.

Marcas e imagens pertencem aos respectivos titulares e não são relicenciadas como código aberto. Estudo independente de Gabriel Duarte, sem vínculo ou endosso de Formula 1 ou das equipes.
