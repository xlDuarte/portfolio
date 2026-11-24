# Auditoria técnica e plano de aprofundamento científico

Data: 24/11/2026. Escopo: os 111 projetos do repositório e as ferramentas do site.

## 1. Diagnóstico

| Medida | Valor | Como foi medido |
|---|---|---|
| Projetos | 111 | `projetos/*/*/` |
| Mediana de linhas no `main.py` | 13 | contagem de linhas; o `main.py` só chama um motor compartilhado |
| Linhas de Python dos motores #001–#100 | ≈ 3 300 | `analytics_batch1` a `advanced_batch`, 10 motores |
| Lógica própria por projeto (#001–#100) | ≈ 20 a 50 linhas | uma função ou um ramo `if project == n` por projeto |
| Dados | 100 % sintéticos em #001–#100 | geradores com fórmulas lineares e ruído gaussiano |
| Páginas de caso no site | só texto | nenhum gráfico, equação ou resultado numérico |
| Projetos com física de verdade | #102 (EKF), #109 (replay), parte de #110/#111 | leitura do código |

**Conclusão [Inferência, a partir do código]:** os projetos #001–#100 estão corretos como exercícios auditáveis. Eles validam o esquema, usam baseline e declaram os limites. O defeito científico está no gerador de dados. Quando o alvo é `y = a·x₁ + b·x₂ + ruído`, qualquer modelo "descobre" a fórmula que o próprio gerador escreveu, e o resultado não ensina nada sobre o fenômeno. O salto de nível é trocar esses geradores por **modelos generativos com base física ou estocástica**, como cinemática de rolamento, balanço térmico, filas e processos de falha. Os métodos de análise passam a ser os que a engenharia usa para esses fenômenos, com incerteza quantificada e validação contra solução analítica ou dado real.

## 2. Critérios de "nível máximo" aplicados a cada projeto

1. **Modelo gerador com base física ou estocástica**, com parâmetros nomeados, unidades SI e referência bibliográfica.
2. **Verificação contra solução analítica** em testes automatizados (caso-limite, conservação, propriedade conhecida).
3. **Validação contra dado real** quando existir dado público (OpenF1/FastF1, NASA, INMET, ONS, BCB).
4. **Incerteza quantificada**: intervalo de confiança, preditivo ou conformal, propagação de Monte Carlo, ou covariância de estimadores.
5. **Métrica adequada ao problema**: regras de pontuação próprias (CRPS, log-loss, Brier), calibração, nDCG, curvas de confiabilidade.
6. **Visualização técnica no site**: gráfico do resultado, equações em MathML e, quando o fenômeno for espacial, 3D.
7. **Limites declarados** sem exagero: o que é modelo, o que é medido, o que não foi validado.

## 3. Auditoria projeto a projeto

Legenda de prioridade: **A** = fenômeno físico com dado real disponível; **B** = fenômeno físico ou estocástico bem estabelecido, sem dado real público; **C** = problema de negócio em que o ganho vem de estatística e decisão, não de física.

### 01 · Análise de dados (#001–#010) — motor `analytics_batch1`

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 001 | Treinamento de operadores | ganho pareado com bootstrap | Modelo misto hierárquico (operador ⊂ turno), tamanho de efeito com IC e análise de poder | C |
| 002 | Reposição aftermarket | curva ABC | Demanda intermitente (Croston/SBA, TSB), nível de serviço e estoque de segurança | C |
| 003 | Catálogo técnico | completude de metadados | Sobrevivência do "tempo até revisão" (Kaplan–Meier) e grafo ativo↔documento | C |
| 004 | Espectro NVH | FFT simples | Sinal de máquina rotativa com frequências de defeito de rolamento (BPFO/BPFI/BSF/FTF), análise de envelope, kurtograma espectral, ordem × rotação (Campbell) | A |
| 005 | Trilhas de capacitação | engajamento médio | Curva de esquecimento de Ebbinghaus e cadeia de Markov de progressão | C |
| 006 | Portal B2B | KPIs de pedido | Funil como processo de Markov absorvente com IC por bootstrap | C |
| 007 | Compras OEM/Tier-1 | agregações | Processo de Poisson não homogêneo por cliente e detecção de mudança (CUSUM) | C |
| 008 | Utilidades por turno | consumo médio | Balanço de energia (ar comprimido, vapor), regressão por graus-dia (ASHRAE Guideline 14, CV-RMSE) | B |
| 009 | Valor de ativos | depreciação linear | Depreciação estocástica, vida útil por Weibull e VPL com Monte Carlo | C |
| 010 | Disrupções da cadeia | impacto agregado | Propagação em rede de fornecedores (grafo) e simulação de eventos discretos de tempo de recuperação | B |

### 02 · EDA (#011–#020) — motor `analytics_eda`

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 011 | Frota e eletrificação | distribuições | Curva logística/Bass de difusão de VE ajustada com IC | B |
| 012 | Segurança e ergonomia | dispersão | Regressão binomial negativa para quase-acidentes (sobredispersão testada) | C |
| 013 | Armazéns | ocupação por hub | Teoria de filas M/M/c para docas, lei de Little verificada nos dados | B |
| 014 | Tempos de volta | boxplot por composto | Degradação de pneu e efeito combustível separados por modelo misto, com dados reais FastF1 | A |
| 015 | Qualidade de lotes | taxa de defeito | Cartas p/u de Shewhart, capacidade Cp/Cpk com IC e modelo beta-binomial | B |
| 016 | SMED / pit stop | tempos de setup | Decomposição interno/externo, distribuição lognormal e caminho crítico (PERT) | B |
| 017 | Mercado de talentos | contagens | Rede de coocorrência de competências e centralidade | C |
| 018 | Ações aço/auto | volatilidade simples | GARCH(1,1), VaR/ES com backtest de Kupiec | B |
| 019 | Despacho de peças | lead time médio | Distribuição de lead time (lognormal vs gama por AIC) e quantis de SLA | C |
| 020 | Atrasos de frete | causas-raiz | Modelo de sobrevivência com riscos competitivos por causa | C |

### 03 · Regressão (#021–#030) — motor `regression_batch` (Ridge × XGBoost, conformal)

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 021 | CAPEX de instalações | Ridge/XGB | Modelo de custo paramétrico por lei de potência (regra dos seis décimos) com intervalo preditivo | C |
| 022 | Valor residual de frota | Ridge/XGB | Depreciação exponencial com efeito de quilometragem e saúde de bateria por modelo de envelhecimento (Arrhenius + ciclos) | B |
| 023 | Custo de mão de obra | Ridge/XGB | Regressão quantílica e decomposição de Oaxaca–Blinder | C |
| 024 | Proficiência em certificação | Ridge/XGB | Teoria de resposta ao item (2PL) | C |
| 025 | Custo de saúde ocupacional | Ridge/XGB | Modelo de frequência × severidade (Poisson × gama), Tweedie | C |
| 026 | Prêmio de seguro | Ridge/XGB | GLM Tweedie com exposição, prêmio puro e carregamento | C |
| 027 | Vendas de forjados | lags | Modelo de espaço de estados e previsão probabilística | C |
| 028 | Custo de hardware edge | Ridge/XGB | Regressão hedônica com efeitos de geração (lei de Moore como prior) | C |
| 029 | Consumo de fornos e usinagem | Ridge/XGB | Balanço térmico do forno (condução, convecção e radiação nas paredes, perda por abertura de porta) e energia específica de corte (Kienzle) | A/B |
| 030 | ETA logístico | Ridge/XGB | Tempo de viagem com distribuição condicional (regressão quantílica) e calibração de cobertura | C |

### 04 · Classificação (#031–#040) — motor `classification_batch` (logística × HGB)

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 031 | Churn B2B | logística/HGB | Sobrevivência (Cox, Weibull AFT), CLV condicionado ao risco | C |
| 032 | Crédito de fornecedor | logística/HGB | Scorecard WoE/IV, calibração, KS e Gini com IC | C |
| 033 | Risco de contraparte | logística/HGB | Modelo PD/LGD/EAD e perda esperada | C |
| 034 | Turnover | logística/HGB | Riscos competitivos (saída voluntária × involuntária) | C |
| 035 | Alertas de segurança TI/OT | logística/HGB | Entropia de Shannon de payload, detecção por Isolation Forest × autoencoder, custo assimétrico | C |
| 036 | Falha em bombas | logística/HGB | Física de falha: curva da bomba (H–Q), cavitação por NPSH disponível × requerido, vibração por ISO 10816 | A/B |
| 037 | Degradação de lubrificante | logística/HGB | Cinética de oxidação de Arrhenius, viscosidade por Walther (ASTM D341), contagem de partículas ISO 4406 | B |
| 038 | Fraude em compras | logística/HGB | Lei de Benford com teste χ² e MAD de Nigrini, e redes de fornecedor | C |
| 039 | Recompra de peças | logística/HGB | BG/NBD + gama-gama | C |
| 040 | Quebra de SLA | logística/HGB | Probabilidade calibrada e decisão por custo esperado | C |

### 05 · NLP (#041–#050) — motor `nlp_batch` (TF-IDF + logística)

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 041–047, 049 | Classificadores de texto | TF-IDF + logística | Embeddings de sentença, comparação com baseline por teste de McNemar, calibração e IC por bootstrap; corpus maior e anotado com protocolo | C |
| 048 | Conformidade ética | regras | Regras com cobertura medida e matriz de confusão por regra | C |
| 050 | Sumarização de normas | extrativa | TextRank com ROUGE e BERTScore contra resumos de referência | C |

### 06 · Recomendação (#051–#060) — motor `recommendation_batch`

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 051, 053, 055, 057 | Conteúdo | TF-IDF + cosseno | Avaliação offline com nDCG@k, MAP e cobertura, e protocolo de divisão temporal | C |
| 052 | Assinaturas acústicas | espectral | Correspondência por MFCC e distância DTW; liga com #004 | B |
| 054, 058, 060 | Peças, fornecedores, kits | vizinhança | Fatoração de matrizes implícita (ALS) e otimização de kit como problema de mochila | C |
| 056 | Alocação de engenheiros | correspondência | Problema de atribuição (húngaro) com restrições | C |
| 059 | Rotas e modais | ranqueamento | Caminho mínimo multicritério e frete por modal com emissões | B |

### 07 · Séries temporais (#061–#070) — motor `timeseries_batch` (Holt-Winters)

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 061 | Preço de aço | Holt-Winters | Dado real (índices públicos), SARIMAX e previsão probabilística com CRPS | A |
| 062 | S&OP | Holt-Winters | Hierarquia com reconciliação MinT | C |
| 063 | Clima na planta | Holt-Winters | Dado real INMET, graus-dia e modelo térmico RC do galpão | A |
| 064 | Demanda de energia na ponta | Holt-Winters | Dado real ONS, regressão harmônica dinâmica | A |
| 065 | Tráfego IIoT | Holt-Winters | Processo de Poisson modulado por Markov | B |
| 066 | Ferramentaria | Holt-Winters | Desgaste de ferramenta pela equação de Taylor (VTⁿ = C) e demanda derivada | B |
| 067 | Ocupação de centros | Holt-Winters | Filas G/G/c e previsão com intervalos | B |
| 068 | Câmbio | Holt-Winters | Dado real BCB/PTAX, GARCH e passeio aleatório como baseline honesto | A |
| 069 | Emissões ESG | Holt-Winters | Pluma gaussiana de dispersão (Pasquill–Gifford) e fatores de emissão | B |
| 070 | Insumos químicos | Holt-Winters | Cinética de consumo por banho (primeira ordem) e reposição (s, S) | B |

### 08 · Visão computacional (#071–#080) — motor `vision_batch` (OpenCV, CNN pequena)

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 071 | EPI | CNN em cena artificial | Avaliação com IoU/mAP e análise de viés de iluminação | C |
| 072 | Gestos | matchShapes | Momentos de Hu com invariância testada | C |
| 073 | Contagem de peças | contornos | Transformada de distância + watershed e erro de contagem com IC | B |
| 074 | Fadiga | abertura do olho | Razão de aspecto do olho (EAR) e PERCLOS | B |
| 075 | OCR em punção | Tesseract | Fotometria de relevo (shape from shading) para gravação | B |
| 076 | Trincas e porosidade | limiar | Filtro de Frangi (Hessiana) para trincas e estatística de poros | B |
| 077 | Sinalização AGV | HSV + polígonos | Geometria projetiva (homografia) e distância estimada | B |
| 078 | Sucata | histograma de cor | Classificação espectral e matriz de confusão | C |
| 079 | Pátio | centroides | Filtro de Kalman + algoritmo húngaro (SORT) | B |
| 080 | Metalografia | CNN | Tamanho de grão ASTM E112 (intercepto), Hall–Petch para estimar resistência | A/B |

### 09 · BI e finanças (#081–#090) — motor `business_batch`

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 081 | LTV | RandomForest | BG/NBD + gama-gama com IC | C |
| 082 | OEE | agregação | Decomposição de perdas (6 grandes perdas) e carta de controle | C |
| 083 | ROI de campanha | grupos aleatorizados | Inferência causal: diferença em diferenças, poder estatístico | C |
| 084 | ABC/RFM | regras | Clusterização com validação (silhueta, estabilidade por bootstrap) | C |
| 085 | Auditoria SOX | regras | Benford, amostragem estatística de auditoria (MUS) | C |
| 086 | Matriz de risco | heatmap | Simulação de Monte Carlo de perda agregada (frequência × severidade) | C |
| 087 | Portfólio CAPEX | seleção por VPL | Programação inteira com incerteza (VPL estocástico, fronteira risco × retorno) | C |
| 088 | Conciliação | previsão | Reconciliação como problema de atribuição, previsão com intervalos | C |
| 089 | Spend analytics | Pareto | Índice HHI, curva de Lorenz/Gini e risco de concentração | C |
| 090 | Custos e tarifa | apuração | Otimização de despacho de carga na tarifa horossazonal (PL) | B |

### 10 · Sistemas avançados (#091–#100) — motor `advanced_batch`

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 091 | Risco de fornecedores | regras | Rede bayesiana de risco | C |
| 092 | Anomalias ERP | IsolationForest | Detecção sequencial (CUSUM, Page–Hinkley) com ARL medido | C |
| 093 | Competências | correspondência | Atribuição ótima e grafo de habilidades | C |
| 094 | Demanda e estoque | previsão + ponto de reposição | Política (s, S) otimizada por simulação, demanda intermitente | B |
| 095 | Retenção B2B | classificação | Sobrevivência + uplift | C |
| 096 | Setup MES | sugestão | Planejamento de experimentos (DOE) e superfície de resposta | B |
| 097 | RUL | regressão supervisionada | Degradação física: crescimento de trinca de Paris–Erdogan, processo gama, Weibull; RUL com IC; dados reais NASA C-MAPSS | A |
| 098 | Documentos | TF-IDF | Avaliação com IC e embeddings | C |
| 099 | Qualidade e segurança | fila de alarmes | Teoria de alarmes (ISA-18.2): taxa, inundação, prioridade | C |
| 100 | BI corporativo | SQL + API | Modelo dimensional e testes de qualidade de dados | C |

### 11 · Motorsport e MLOps (#101–#111)

| # | Projeto | Hoje | Salto científico proposto | Prior. |
|---|---|---|---|---|
| 101 | Estratégia e pit stop | simulador de janela | Programação dinâmica estocástica com degradação, combustível, tráfego e safety car (Poisson) | A |
| 102 | EKF de dinâmica veicular | EKF bicicleta | Modelo de bicicleta não linear com pneu Pacejka, UKF × EKF, consistência NEES/NIS | A |
| 103 | Visão onboard | fluxo óptico | Calibração de câmera e estimativa de movimento com incerteza | B |
| 104 | Vibração LSTM | LSTM × baseline | Sinal físico de rolamento (mesmo gerador de #004), envelope e dado real (CWRU) | A |
| 105 | Raio-X NDT | CNN + Grad-CAM | Atenuação de Beer–Lambert para gerar radiografia física de poros e trincas | B |
| 106 | MLOps | MLflow/FastAPI | Monitoramento de deriva (PSI, KS) com limiares estatísticos | C |
| 107 | RAG industrial | recuperação | Avaliação de recuperação (recall@k, MRR) com conjunto anotado | C |
| 108 | SHAP + SMOTE | SHAP | Calibração pós-SMOTE e comparação com pesos de classe | C |
| 109 | Replay F1 | replay | Interpolação por spline na distância percorrida e sincronização de tempo | A |
| **110** | **Engenharia de performance** | **fórmulas ilustrativas ("proxy QSS")** | **Pneu Pacejka MF, transferência de carga, envelope GGV, simulador QSS na geometria real do Bahrein, calibração e validação contra a telemetria de Verstappen, modelo térmico do pneu** | **A** |
| 111 | F1 PIP | Monte Carlo + ML | Pace bayesiano hierárquico (piloto, equipe, composto) e calibração das probabilidades | A |

## 4. Fases de execução (uma PR por fase)

| Fase | Tema | Projetos | Por que nessa ordem |
|---|---|---|---|
| **1** | **Dinâmica veicular e simulador de volta** | **#110, ferramenta de tempo de volta; base para #101, #102, #014** | **Nicho principal, dado real disponível e física mais pesada** |
| 2 | Estratégia de corrida e pace bayesiano | #101, #111, #014 | Reusa o modelo de pneu e degradação da fase 1 |
| 3 | Estimação de estado | #102, #109 | Reusa o modelo de bicicleta com Pacejka |
| 4 | Física de falha e confiabilidade | #004, #036, #037, #097, #104, #052 | Um gerador de rolamento e degradação comum, com dado real (CWRU, C-MAPSS) |
| 5 | Energia, térmica e ambiente | #008, #029, #063, #064, #069, #070, #090 | Balanços de energia e dado público (INMET, ONS) |
| 6 | Materiais e visão física | #076, #080, #105, #073, #079, #074, #077, #075 | Geração física de imagem (Beer–Lambert, microestrutura) |
| 7 | Operações e cadeia de suprimentos | #002, #010, #013, #016, #019, #020, #059, #060, #066, #067, #094, #096 | Filas, estoque e simulação de eventos discretos |
| 8 | Séries temporais e finanças com dado real | #018, #061, #062, #065, #068, #027 | Previsão probabilística e risco |
| 9 | Estatística aplicada a negócio | #001, #003, #005–#007, #009, #011, #012, #015, #017, #021–#028, #030–#035, #038–#040, #081–#089, #091–#093, #095, #098–#100 | GLM, sobrevivência, inferência causal e calibração |
| 10 | NLP, recomendação e MLOps | #041–#051, #053–#058, #106–#108 | Protocolos de avaliação com IC |
| 11 | Páginas de caso com resultado | todos | Gráfico SVG gerado no build, equações em MathML e números reproduzíveis em cada página |

A fase 11 avança junto com as outras: cada fase já publica as páginas dos projetos que tocou.

## 5. Riscos e limites

| Risco | Mitigação |
|---|---|
| Parecer validação sem dado real | Toda página separa "verificado contra solução analítica", "validado contra dado real" e "não validado" |
| Inflar o peso das páginas | Gráficos em SVG estático gerado no build; JavaScript e 3D só nas ferramentas interativas |
| Parâmetros de carro de equipe são secretos | Usar faixas publicadas na literatura e calibrar só o que a telemetria pública identifica; declarar o que não é identificável |
| Volume de trabalho | Uma fase por PR, cada uma com testes e capturas |
