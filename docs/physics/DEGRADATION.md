# Degradação com dados reais: vida útil restante (C-MAPSS), vazamento de bomba e óleo (banco hidráulico ZeMA)

Fase 4b do [plano científico](../PLANO-CIENTIFICO.md). Projetos #097, #036 e #037.

| Projeto | Dados | Página |
|---|---|---|
| #097 Manutenção preditiva | NASA C-MAPSS FD001 e FD003 (versionados em `data/cmapss/`, domínio público) | [/cases/advanced/097/](https://gabriel-automotive-industrial-lab.vercel.app/cases/advanced/097/) |
| #036 Falha de bomba hidráulica | Banco hidráulico da ZeMA, UCI, CC BY 4.0 (`scripts/fetch_hydraulic.py`) | [/cases/classification/036/](https://gabriel-automotive-industrial-lab.vercel.app/cases/classification/036/) |
| #037 Degradação de lubrificante | Temperaturas do mesmo banco | [/cases/classification/037/](https://gabriel-automotive-industrial-lab.vercel.app/cases/classification/037/) |

Código: [`degradation/`](../../degradation/). Dados do site: `python scripts/build_degradation_data.py` (≈ 50 s) → `site/data/degradation.json`. Navegador: [`frontend/science/degradation.js`](../../frontend/science/degradation.js).

---

## 1. Procedência

**C-MAPSS.** Os sites da NASA não são acessíveis a partir do ambiente de build. Os arquivos vêm do espelho `edwardzjl/CMAPSSData` (commit `ed40e40`), que traz também o `readme.txt` e o artigo de Saxena et al. do pacote original. Conferências: número de linhas e motores igual ao publicado (FD001: 20.631 linhas de treino, 13.096 de teste, 100 motores em cada; FD003: 24.720 e 16.596). O `readme.txt` da NASA troca as contagens do FD004 (diz 248 de treino e 249 de teste; os arquivos têm 249 e 248). FD001 e FD003 ficam versionados em gzip, com o SHA-256 do texto original em `data/cmapss/manifest.json`, verificado por teste.

**Banco hidráulico.** Arquivos brutos do conjunto da UCI (2.205 ciclos de 60 s; ≈ 730 MB de texto) vindos do espelho `YoverCC/Project-Data-hydraulicsystemuci` (commit `39834e5`). Um segundo espelho independente (`fahadijaz/…`, commit `ae2cff4`) tem os mesmos identificadores de blob git para PS1, FS1, EPS1, TS1 e `profile.txt`. Os 20 arquivos usados têm SHA-256 em `data/hydraulic/manifest.json`; o cache derivado (8 MB) fica fora do git e 36 ciclos (um por combinação bomba × resfriador × válvula) ficam em `tests/fixtures/`. As contagens de rótulos batem com a documentação (bomba: 1.221 / 492 / 492; resfriador 732 / 732 / 741; válvula 1.125 / 360 / 360 / 360; acumulador 599 / 399 / 399 / 808).

---

## 2. #097 — vida útil restante

**Indicador de saúde.** Regressão linear dos 14 sensores que variam com a degradação (2, 3, 4, 7, 8, 9, 11, 12, 13, 14, 15, 17, 20, 21), padronizados, contra 0 nos primeiros 10 % e 1 nos últimos 10 % da vida de cada motor de treino.

**Trajetória aleatória.**

    S_i(t) = a_i + b_i (e^{γ_i t} − 1)/γ_i + ε,   (a_i, ln b_i, ln γ_i) ~ N(μ₀, Σ₀)

μ₀ e Σ₀ vêm dos ajustes por motor no treino (γ por busca em grade, a e b por mínimos quadrados). O ruído σ é inflado por √((1 + ρ)/(1 − ρ)), com ρ a autocorrelação de defasagem 1 dos resíduos. Limiar de falha D ~ N(m_D, s_D²), dos valores ajustados no instante da falha. Posteriori de um motor de teste por amostragem por importância com proposta de Laplace (moda por Nelder–Mead, hessiana numérica, covariância × 2); menor tamanho efetivo de amostra entre os 200 motores de teste: 88 (mediana ≈ 4.400). Cada sorteio (θ, D) dá um instante de falha.

**Escolha do modelo** (CRPS médio em validação cruzada de 5 dobras por motor, trajetórias de treino cortadas em pontos aleatórios):

| Candidato | FD001 | FD003 |
|---|---|---|
| γ comum = 0,01 | 21,1 | 31,5 |
| γ comum = 0,02 | 13,3 | 22,6 |
| γ comum = 0,03 | 18,2 | 28,1 |
| **γ próprio de cada motor** | **9,9** | **19,8** |

**Resultado nos motores de teste oficiais** (a vida restante real só entra aqui):

| | FD001 bayesiano | FD001 ridge | FD003 bayesiano | FD003 ridge |
|---|---|---|---|---|
| RMSE geral (ciclos) | 19,3 | 19,1 | 44,5 | 19,2 |
| RMSE com vida restante < 60 | **5,7** | 14,1 | **9,0** | 17,5 |
| RMSE com vida restante 60–120 | 24,8 | 17,5 | 46,7 | 17,8 |
| RMSE com vida restante ≥ 120 | 22,1 | 32,7 | 75,1 | 24,6 |
| Escore PHM 2008 | 2.150 | 559 | 2,9 × 10¹¹ | 681 |
| CRPS | 9,0 | — | 16,4 | — |
| Cobertura 90 % / 50 % | 92 % / 44 % | — | 86 % / 46 % | — |

Ridge: regressão em média e inclinação da janela de 20 ciclos do indicador e de cada sensor, com o alvo linear por partes min(125, RUL) (Heimes, 2008). Esse teto encaixa no desenho do conjunto de teste (vida restante real ≤ 145) e dá ao ridge o menor erro geral. O modelo bayesiano é muito melhor perto da falha e calibrado no FD001. No FD003, os motores sem desgaste visível recebem a vida típica de uma frota cujas vidas vão de 145 a 525 ciclos; a mediana fica tarde demais e o escore PHM, que pune exponencialmente o atraso, explode. O indicador linear único também descreve mal a mistura de dois modos de falha.

**Decisão de manutenção.** A cada motor de teste, intervir na janela de 30 ciclos se P(RUL ≤ 30) ≥ 1/10 (custo de falha = 10 × custo de intervenção, hipótese):

| Política | FD001 intervenções / falhas / custo | FD003 |
|---|---|---|
| Bayesiana | 26 / 0 / 26 | 24 / 0 / 24 |
| Ridge (previsão ≤ 30) | 14 / 11 / 124 | 12 / 8 / 92 |
| Informação perfeita | 25 / 0 / 25 | 20 / 0 / 20 |
| Nunca intervir | 0 / 25 / 250 | 0 / 20 / 200 |

**Weibull das vidas de treino** (MLE, IC 95 % pela informação observada): FD001 k = 4,41 [3,80; 5,01], λ = 225 ciclos, B10 = 135; FD003 k = 2,93 [2,52; 3,33], λ = 277, B10 = 128. O teste KS rejeita a Weibull nos dois (p = 0,013 e 0,017; conservador, pois os parâmetros foram estimados nos mesmos dados): as vidas têm cauda direita mais longa.

---

## 3. #036 — vazamento interno da bomba

**Patamares.** PS1 (100 Hz) e EPS1 (100 Hz) médios a 10 Hz para casar com FS1. Amostras com |Δp| < 0,3 bar, 1 s após cada degrau, vazão > 2 L/min, fora do trecho de alívio (≈ 191 bar, vazão nula). Por ciclo: regressão da vazão na pressão, lida a 156 bar; eficiência hidráulica η = Σ p·Q / 600 / Σ P_el (kW).

**Viscosidade.** Walther (ASTM D341) por ν₄₀ = 46 e ν₁₀₀ = 6,8 mm²/s (óleo suposto ISO VG 46, IV ≈ 100). Bomba sã: Q = Q_th − K/ν(T).

**Teste fora da amostra.** Ajustado em ciclos estáveis de bomba sã com óleo a 35,3–45,8 °C (resfriador a 20 % e 100 %): Q_th = 7,960 L/min, K = 5,92. Previsto para os ciclos a 56,2 °C (resfriador a 3 %): 7,710 L/min; medido: 7,707 (média), 7,673 (mediana). Uma reta em temperatura prevê 7,733.

**Natureza do vazamento.** K ajustado por nível de vazamento: 5,92 (sem), 8,92 (leve), 9,23 (severo). Um orifício turbulento não dependeria da viscosidade; o aumento de K mostra que parte da vazão perdida é laminar.

**Classificação** (logística multinomial L2, acurácia balanceada; compensação ajustada só no treino de cada dobra):

| Atributos | Ciclos sorteados 70/30 | Regime térmico novo (deixa um estado do resfriador de fora) |
|---|---|---|
| Estatísticos (média e desvio dos 17 canais) | 84,7 % | 59,5 % (65 / 65 / 49 %) |
| Físicos sem compensação (vazão a 156 bar, inclinação, η, T) | 99,4 % | 81,8 % (53 / 100 / 93 %) |
| Físicos com compensação (déficit de vazão, η, T) | 98,7 % | **94,0 %** (94 / 100 / 88 %) |

O resfriador muda só duas vezes no ensaio, então cada estado é um bloco contínuo de ciclos e uma faixa de temperatura do óleo (36, 45 e 55 °C). A compensação de viscosidade é o que permite generalizar para a temperatura não vista; sem ela, o modelo físico falha justamente no óleo quente (53 %).

Déficit de vazão mediano (L/min), sem / leve / severo: 0,04 / 0,21 / 0,32 a 55 °C; 0,00 / 0,25 / 0,37 a 45 °C; 0,00 / 0,23 / 0,35 a 36 °C. Eficiência hidráulica a 36 °C: 82,4 % → 79,7 % → 77,9 %.

---

## 4. #037 — viscosidade e oxidação do óleo

Temperatura média do óleo (TS1) por estado do resfriador: 55,0 °C (3 %), 45,5 °C (20 %), 36,0 °C (100 %). Viscosidade média: 25,0 / 36,2 / 55,7 mm²/s. Oxidação relativa a 40 °C (Arrhenius), com E_a = 50 / 66 / 80 kJ/mol: 2,42 / 3,22 / 4,16 × (3 %), 1,40 / 1,56 / 1,71 × (20 %), 0,78 / 0,72 / 0,67 × (100 %). E_a = 65,9 kJ/mol é a energia que dobra a taxa entre 60 e 70 °C (a regra prática dos 10 °C).

A viscosidade é sustentada pelos dados (seção 3: a previsão da vazão no óleo quente). A oxidação é uma estimativa: o conjunto de dados não tem análise de óleo (acidez, água, partículas pela ISO 4406), e o classificador sintético original continua na página como teste do pipeline.

---

## 5. Testes (`tests/test_degradation.py`)

Manifesto do C-MAPSS conferido; tamanhos publicados; indicador de saúde de 0 a 1; CRPS de uma normal padrão; assimetria do escore PHM; MLE da Weibull recupera parâmetros; o modelo de degradação, aplicado a uma frota simulada por ele mesmo, cobre a verdade com seus intervalos; Walther passa pelos pontos de referência; Arrhenius dobra em 10 °C; a compensação recupera um modelo conhecido; no trecho real, a vazão e a eficiência caem com o vazamento.

## Referências

- Saxena, A., Goebel, K., Simon, D. e Eklund, N. Damage propagation modeling for aircraft engine run-to-failure simulation. *PHM 2008*.
- Wang, T., Yu, J., Siegel, D. e Lee, J. A similarity-based prognostics approach for remaining useful life estimation of engineered systems. *PHM 2008*.
- Heimes, F. O. Recurrent neural networks for remaining useful life estimation. *PHM 2008*.
- Gebraeel, N., Lawley, M., Li, R. e Ryan, J. Residual-life distributions from component degradation signals: a Bayesian approach. *IIE Transactions* 37(6), 2005.
- Helwig, N., Pignanelli, E. e Schütze, A. Condition monitoring of a complex hydraulic system using multivariate statistics. *I2MTC 2015*.
- ASTM D341: Standard practice for viscosity–temperature equations and charts for liquid petroleum or hydrocarbon products.
- Gneiting, T. e Raftery, A. E. Strictly proper scoring rules, prediction, and estimation. *JASA* 102, 2007.
