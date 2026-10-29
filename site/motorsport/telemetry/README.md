# Telemetria / EKF — projeto 102

Página canônica: `/cases/motorsport/102/`. O hub encaminha o projeto 102 para esta página; nenhum segundo laboratório é montado. CSS e comportamento isolados. Gráficos ECharts 6.0.0 usam a distribuição local licenciada já presente em `../replay/vendor`; SVG mantém visualizações e inspeção temporal disponíveis quando a biblioteca falha.

## Modelo

`model.mjs` chama `ekf()` de `../lab/engine.mjs` sem alterar o motor compartilhado. Tempo: 200 amostras, intervalo de 0,02 s, 0 a 3,98 s. Ruído em m/s², Q em rad², ângulos exportados e exibidos em graus. O estimador é escalar, com observação linear, velocidade fixa de 62 m/s, H = −95, R = 0,0025 e semente 102. A mesma aceleração alimenta predição e correção. Não é uma implementação validada de EKF veicular não linear.

Controles: ruído 0–3; Q 10⁻⁶–10⁻³ em escala logarítmica; cenários de ruído; visibilidade de sinais; inspeção de amostras; reprodução 0,25×/0,5×/1×; reinício; restauração; JSON. Reprodução pausa ao ocultar a página e ao alcançar o final.

RMSE, MAE, máximo absoluto e redução do RMSE usam todas as amostras, incluindo o transiente inicial. Redução = 100 × (1 − RMSE_filtro / RMSE_sensor); quando o denominador é numericamente zero, o valor é nulo. Não se mascara redução negativa. Histograma usa 16 intervalos comuns e conserva 200 observações em cada série. Esquema do veículo amplia o ângulo em 12×, explicitamente sinalizado. Não mostra uma trajetória real nem confiança estatística.

## Verificação

`node tests/telemetry_checks.mjs`

`python -m unittest discover -s tests -p test_telemetry.py`

Testes cobrem paridade completa com o motor, métricas, eixo temporal, determinismo, conservação das contagens, limites e condição sem ruído. Verificação de navegador realizada em 1440, 768 e 390 px: biblioteca local, controles, clique no gráfico, reprodução/pausa/fim, restauração, visibilidade, exportação, fallback e redirecionamento do hub. A captura 102.webp é produzida pela interface em funcionamento.

## Evoluções futuras

Validar um modelo não linear multivariável contra dados de sensores com unidades e sincronização verificadas; separar ruídos de processo e medição; calibrar Q/R; incluir inovação, covariância e testes de consistência estatística antes de apresentar intervalos de confiança. Estas evoluções não fazem parte do redesign.
