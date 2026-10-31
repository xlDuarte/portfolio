# Fontes reais — migração de dados Motorsport

## Origem e escopo

As páginas anteriormente executavam geradores sintéticos. O novo caminho público usa dados observados e identifica processamento e previsões separadamente. Os motores didáticos antigos continuam no repositório para reprodutibilidade histórica/testes, mas não são a fonte dos painéis migrados. A página principal e a página de indústria não foram alteradas.

- OpenF1: sessão 9472, Bahrain, corrida de 02/03/2024. 20 pilotos, 1129 registros de volta; 4 minutos de car_data/location de VER, PER e SAI entre 15:05:30 e 15:09:30 UTC. Não é replay completo nem ao vivo.
- FastF1 3.9.0 / cliente Jolpica: resultados completos paginados de 2022, 2023 e 2024, com verificação de contagem e duplicidade.
- O acesso direto ao timing via Session.load encontrou exigência de autenticação nesta execução. Nenhuma credencial foi solicitada, armazenada ou embutida. O replay usa a fonte complementar OpenF1 explicitamente, não é rotulado como telemetria coletada por FastF1.
- Os manifestos registram URL, SHA-256 e data de coleta/geração. Cache em `.cache/f1-public` não faz parte da publicação.

## Comportamento por projeto

| Projeto | Dados e comportamento |
|---|---|
| 101 Pneus | Regressão exploratória de 1004 voltas observadas; contrafactuais S-H e S-H-S. Parada é hipótese do usuário; não confundir pit duration com perda líquida. |
| 102 Telemetria | Velocidade/RPM/acelerador/freio/marcha reais. Suavização Kalman escalar com Δt real. Resíduo não é erro contra verdade-terreno. EKF de sideslip não é executado sem sensores necessários. |
| 103 Visão | Sem vídeo onboard autorizado. Execução sintética retirada; aguardando aquisição. |
| 104 Vibração | Sem acelerômetro público de alta frequência. Importação CSV local de aquisição, sem diagnóstico de falha inventado. |
| 105 Radiografia | Sem dataset de radiografias F1 autorizado; análise indisponível. |
| 106 MLOps | Registro dos oito modelos reais e distribuições históricas. Não anuncia serviço FastAPI/MLflow hospedado. |
| 107 RAG | Sem corpus técnico versionado validado; nenhuma resposta é fabricada. |
| 108 SHAP | Direciona para métricas reais; não alega valores SHAP não calculados. |
| 109 Replay | Recorte observado, timestamps UTC, posições do canal position. Sem gaps fictícios ou ajuste de aderência que altere medições. Aceleração é derivada. |
| 110 Porsche | Identidade preservada; dados F1 não são dados Porsche. Importação local de cargas/temperaturas/acelerações; sem aquisição pré-carregada. |
| 111 Modelos | Oito algoritmos, treino 2022 / validação 2023; ajuste final 2022+2023 para retrospectiva pré-corrida Bahrain 2024. |

## Validade científica

Features: grid, média dos últimos cinco resultados do piloto e do construtor. Na primeira observação, prior explícito de posição 10,5. Construtor usa últimos cinco resultados individuais, não cinco GPs. Atualização somente após cada corrida. Ranking compara classificações finais; não há modelo de abandono separado. Modelos: grid, forma recente, Ridge, regressão linear, Random Forest, Extra Trees, Gradient Boosting e HistGradientBoosting. Temperatura 5 pré-fixada para log-loss, sem ajuste/calibração; Monte Carlo Plackett–Luce é inferência estocástica sobre escores reais treinados. Modelo selecionado pelo MAE de 2023; esse período não é avaliação independente da seleção.

A estratégia usa efeitos de piloto, composto, idade e volta. Associação de volta não é combustível medido. Filtro de duração explícito 88–104s e remoção de primeiras/últimas voltas de stint/pit-out; resultados são ajustes nesta corrida, sem alegação causal ou prospectiva. Covariâncias Q/R do filtro são hipóteses ajustáveis. Velocidade publicada tem frequência e resolução limitadas; derivadas amplificam quantização. A posição é aproximada e usa última amostra, com sinalização de dado desatualizado.

## Reprodução

```bash
python -m pip install -r requirements-real-f1.txt
python scripts/collect_f1_real.py
python scripts/fit_f1_strategy.py
python scripts/train_f1_real.py
python -m unittest discover -s tests -p test_real_f1.py -v
```

Não existe fallback sintético quando uma fonte falha. A última versão validada permanece publicável; uma falha de coleta impede sua substituição. Os coletores atuais são explícitos para este recorte histórico, não prometem todas as temporadas/sessões nem atualizações ao vivo.

## Limites ainda abertos

Adquirir vídeos/sensores/Porsche/imagens/corpus autorizados para projetos 103/104/105/107/108/110; expandir coleta para sessões configuráveis e grid completo; avaliação temporal externa independente, calibração e DNF; EKF veicular exige IMU e referência física. Não se pode declarar todos esses projetos convertidos em análises reais executáveis enquanto os dados faltam.
