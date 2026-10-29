# Replay F1 — melhorias futuras

Registrado em 29/10/2026. Backlog para uma próxima etapa; não implementado nesta entrega.

A etapa visual publicada inclui pista 2D/3D, classificação, seleção de piloto, reprodução, linha do tempo, gráficos sincronizados e exportação. O motor atual é sintético.

## Prioridade 1 — uma sessão real em um circuito real
- Definir fonte, licença e formato de importação de sessões, pilotos, voltas e posições.
- Carregar um traçado real com coordenadas e escala verificadas.
- Sincronizar tempo da sessão, voltas, posições e telemetria; tratar amostras ausentes sem inventar medições.
- Exibir origem, sessão, unidades, qualidade e limitações dos dados.
- Aceite: reproduzir uma sessão completa e conferir os resultados com a fonte.

## Prioridade 2 — coerência física e eventos
- Tornar deslocamento, velocidade e aceleração consistentes. Hoje o deslocamento e a velocidade usam fórmulas independentes e a aceleração deriva do sinal sintético de velocidade.
- Calcular intervalos entre pilotos com uma referência temporal consistente.
- Integrar pit stops, bandeiras e safety car à linha do tempo e à classificação.
- Aceite: validar distâncias e derivadas, transições de volta, entrada e saída de boxes e neutralizações.

## Prioridade 3 — comparação
- Comparar voltas por distância, delta acumulado e setores.
- Diferenciar medição, interpolação e estimativa em gráficos e exportações.
- Aceite: comparar duas voltas completas sem desalinhamento e exportar os dados usados.

Preservar navegação, responsividade, fallback, acessibilidade e isolamento das páginas principal e de indústria. Não apresentar o cenário sintético atual como GPS real, circuito oficial ou modelo físico calibrado.
