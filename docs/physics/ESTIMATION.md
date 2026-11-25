# Estimação de estado, probabilidades calibradas e benchmark corrigido: método, verificação e validação

Fase 3 do [plano científico](../PLANO-CIENTIFICO.md). Três projetos, cada um com um gerador determinístico de dados:

| Projeto | Código | Gerador | Dados | Página |
|---|---|---|---|---|
| #102 Estimação de deriva | [`state_estimation/`](../../state_estimation/) | `python scripts/build_estimation_data.py` (alguns minutos) | `estimation-bahrain.json` | [/cases/motorsport/102/](https://gabriel-automotive-industrial-lab.vercel.app/cases/motorsport/102/) |
| #111 Probabilidades calibradas | [`race_strategy/ranking.py`](../../race_strategy/ranking.py) | `python scripts/build_ranking_data.py` (≈ 1 min) | `ranking-calibration.json` | [/motorsport/f1-pip/](https://gabriel-automotive-industrial-lab.vercel.app/motorsport/f1-pip/) |
| #014 Benchmark de voltas | [`race_strategy/benchmark.py`](../../race_strategy/benchmark.py) | `python scripts/build_benchmark_data.py` (≈ 30 s) | `benchmark-bahrain.json` | [/cases/014/](https://gabriel-automotive-industrial-lab.vercel.app/cases/014/) |

Navegador: [`frontend/science/`](../../frontend/science/), um único ponto de entrada que carrega só o módulo da página.

---

## Parte A — #102: ângulo de deriva com sensores ruidosos

### A.1 Por que simulação

O OpenF1 publica velocidade, rotação, marcha, acelerador, freio e posição, mas não IMU nem volante. Sem guinada e aceleração lateral medidas não existe estimação de deriva com dados reais, e sem uma referência independente de β não existe validação. A alternativa honesta é um estudo de Monte Carlo com verdade conhecida, construído sobre o carro e a pista calibrados na fase 1.

### A.2 Verdade simulada (não é o modelo dos filtros)

Para que o teste não seja circular ("inverse crime"), a verdade é mais rica que o modelo dentro dos filtros:

- **Forças por roda** com transferência lateral de carga (bitola, altura do CG e repartição da rigidez de rolagem), resolvida por um passo de ponto fixo. O filtro só tem forças por eixo.
- **Piloto virtual**: controle de velocidade sobre o perfil QSS calibrado (95 % da velocidade, para manter margem de aderência) e volante = esterço de regime permanente para a guinada de referência da trajetória, mais correção proporcional do erro de guinada e antecipação de 0,15 s. Atuador de primeira ordem com τ = 50 ms.
- **Integração** por RK4 a 500 Hz; sensores amostrados a 50 Hz.
- **Pneu gasto**: o pico da Magic Formula (λ<sub>μy</sub>) cai 10 % na verdade e o filtro não é avisado.

O esterço de regime permanente vem da inversão da Magic Formula por bisseção: dadas v<sub>x</sub> e r, F<sub>yf</sub> = m v<sub>x</sub> r b/ℓ e F<sub>yr</sub> = m v<sub>x</sub> r a/ℓ; o teste `test_steady_state_steer_reproduces_yaw_rate` verifica que esse esterço, integrado, reproduz a guinada pedida.

### A.3 Sensores (hipóteses de ordem de grandeza)

| Sensor | Ruído (1σ) | Observação |
|---|---|---|
| Giroscópio (guinada) | 0,3 °/s | viés inicial 0,5 °/s, passeio aleatório 0,02 °/s/√s |
| Acelerômetro lateral | 0,05 g | |
| Ângulo de volante (na roda) | 0,1° | entrada dos filtros |
| Velocidade das rodas | 0,2 m/s | |

### A.4 Filtros

Estado x = (v<sub>x</sub>, v<sub>y</sub>, r, b<sub>g</sub>); medidas z = (r + b<sub>g</sub>, a<sub>y</sub>, v<sub>x</sub>); entradas u = (δ, a<sub>x</sub>). Modelo de processo: bicicleta não linear com forças por eixo da Magic Formula, cargas com aerodinâmica e transferência longitudinal, um passo de RK4 por amostra. I<sub>z</sub> = 1.200 kg·m² (hipótese).

- **EKF**: jacobianos por diferenças centrais, atualização de Joseph.
- **UKF**: pontos sigma de Van der Merwe, α = 0,5, β = 2, κ = 0.
- **UKF + λ**: estado aumentado com o fator de aderência λ como passeio aleatório (σ = 0,001 por passo). λ escala o pico D da Magic Formula e mantém a rigidez de deriva.
- **Referências**: EKF com pneu linear (rigidez da Magic Formula na origem) e integração direta (β̇ = a<sub>y</sub>/v<sub>x</sub> − r com giroscópio e acelerômetro brutos).

Todos rodam em lote vetorizado: as 40 execuções de Monte Carlo avançam juntas.

**Ruído de processo.** Q = diag(0,05², 0,2², 0,02², (0,02 °/s·√Δt)²) em unidades SI, ajustado no cenário nominal até a mediana do NEES do UKF ficar próxima da faixa χ². Não foi reajustado no cenário gasto, que funciona como teste.

### A.5 Consistência

Com N execuções independentes e n estados, N·ε̄<sub>k</sub> ~ χ²<sub>Nn</sub> se o filtro é consistente (Bar-Shalom, Li e Kirubarajan, *Estimation with Applications to Tracking and Navigation*, 2001, cap. 5). Com N = 40 e n = 4, a faixa de 95 % para ε̄ é 3,17 a 4,92. O NIS usa a inovação e não precisa da verdade (valor esperado 3, o número de medidas).

### A.6 Resultados (volta completa, 40 execuções, primeiro segundo excluído)

Pneu como calibrado:

| Estimador | RMSE de β | Erro máx. | Cobertura ±1,96σ | NEES mediano | Tempo na faixa χ² | NIS médio |
|---|---|---|---|---|---|---|
| Integrador | 28,7° | 133° | — | — | — | — |
| EKF, pneu linear | 0,76° | 2,7° | 50 % | 56 | 6 % | 3,07 |
| EKF, Magic Formula | 0,31° | 1,7° | 65 % | 5,9 | 39 % | 1,50 |
| UKF, Magic Formula | 0,29° | 1,5° | 70 % | 5,3 | 41 % | 1,49 |
| UKF + λ | **0,16°** | 1,6° | 87 % | 4,1 | 70 % | 1,46 |

Pneu 10 % mais gasto, filtro com a aderência calibrada:

| Estimador | RMSE de β | Cobertura | NEES mediano | Tempo na faixa |
|---|---|---|---|---|
| EKF, pneu linear | 0,72° | 49 % | 48 | 9 % |
| EKF, Magic Formula | 0,40° | 59 % | 6,6 | 26 % |
| UKF, Magic Formula | 0,38° | 62 % | 6,0 | 30 % |
| UKF + λ | **0,15°** | 90 % | 3,8 | 71 % |

β verdadeiro: RMS 1,3°, máximo 4,2°; aceleração lateral máxima 2,9 g.

**Leitura.**

1. A integração direta diverge: o viés do giroscópio se acumula sem nada que o corrija.
2. Com pneu linear, o filtro só acerta em curvas leves; no limite, a rigidez linear superestima a força e o filtro fica muito otimista (NEES ≈ 50 com faixa até 4,9).
3. EKF e UKF com Magic Formula têm erro parecido, com vantagem pequena e consistente do UKF. Os dois ficam otimistas porque o modelo de eixo não reproduz a transferência lateral de carga da verdade.
4. Estimar λ junto reduz o erro em 43 % (nominal) e 61 % (gasto) e devolve o NEES à faixa χ² em cerca de 70 % da volta. λ funciona como parâmetro de compensação do erro estrutural.
5. **Queda de aderência**: λ̂ final 0,943 (nominal) e 0,860 (gasto). Queda detectada de 8,8 % contra 10,0 % na aderência equivalente por eixo da verdade (0,916/1,018). O valor absoluto de λ̂ fica abaixo do valor do pneu porque também absorve a transferência lateral de carga; a variação relativa é o dado útil. λ só é observável quando os pneus trabalham perto do limite.

### A.7 Testes (`tests/test_state_estimation.py`)

- Esterço de regime permanente reproduz a guinada pedida em simulação.
- Modelo por eixo e modelo por roda coincidem quando a transferência lateral é zero.
- EKF e UKF coincidem em regime linear.
- Em verdade linear com modelo linear (sem erro estrutural), o NEES médio fica dentro da faixa χ².
- O filtro aumentado recupera um λ conhecido quando a verdade usa o mesmo modelo de eixo.

---

## Parte B — #111: probabilidades de resultado calibradas

### B.1 Modelo

Plackett–Luce com utilidade s<sub>i</sub> = w·x<sub>i</sub>, em que x = −(grid, média das 5 últimas chegadas do piloto, média das 5 últimas da equipe). A verossimilhança das k primeiras posições é côncava em w; o máximo vem de L-BFGS com gradiente analítico e penalização L2 de 10⁻³. Erros-padrão pela hessiana numérica do gradiente. A escala de w faz o papel da temperatura, agora estimada.

Probabilidade de vitória: softmax de s. Pódio e top 10: 20 mil amostras exatas por Gumbel-max (ordenar s<sub>i</sub> + G<sub>i</sub>, G<sub>i</sub> ~ Gumbel(0, 1)).

### B.2 Avaliação

Janela crescente sobre 68 corridas de 2022 a 2024 (FastF1/Jolpica, já no site): cada corrida de 2023 e 2024 (46) é prevista com o modelo ajustado a todas as anteriores, 919 previsões piloto × corrida.

| Modelo | Brier vitória | Log-loss vencedor | Brier pódio | Brier top 10 | ECE vit./pód./top 10 |
|---|---|---|---|---|---|
| Plackett–Luce (MLE, k = 10) | 0,0355 | 1,636 | 0,0775 | 0,140 | 0,036 / 0,056 / 0,061 |
| Plackett–Luce, só grid | 0,0399 | 1,966 | 0,0843 | 0,155 | 0,035 / 0,071 / 0,037 |
| Ridge + softmax T = 5 (método anterior do site) | 0,0403 | 2,020 | 0,0909 | 0,152 | 0,056 / 0,093 / 0,112 |
| Uniforme | 0,0475 | 2,995 | 0,1276 | 0,250 | — |

Redução do Brier do Plackett–Luce, IC 95 % por reamostragem de corridas (4.000 réplicas):

| Referência | Vitória | Pódio | Top 10 |
|---|---|---|---|
| Uniforme | 25,4 % [20,9; 29,7] | 39,3 % [33,5; 44,1] | 44,1 % [36,4; 51,5] |
| Só grid | 11,0 % [7,1; 15,0] | 8,1 % [3,7; 12,2] | 9,8 % [4,1; 15,4] |
| Método anterior | 12,1 % [8,8; 15,4] | 14,8 % [10,5; 18,6] | 7,8 % [3,4; 12,7] |

**Calibração.** Teste de Spiegelhalter: vitória z = −1,49 (p = 0,14), pódio z = −3,57 (p < 0,001), top 10 z = −0,38 (p = 0,70). No pódio as previsões são pouco confiantes nas duas pontas: na faixa de 0–10 % prevista, a frequência foi 1,1 %; na faixa de 50–60 %, foi 78 %.

### B.3 Truncamento da verossimilhança

Uma única utilidade não descreve com o mesmo ruído a disputa pela vitória e a do meio do pelotão. k foi escolhido por mercado só em 2023 (grade 3, 5, 10, 20) e avaliado em 2024:

| Mercado | k escolhido | Brier 2024 (k escolhido) | Brier 2024 (k = 10) | Redução [IC 95 %] |
|---|---|---|---|---|
| Vitória | 3 | 0,0361 | 0,0387 | 6,7 % [−4,2; 18,2] |
| Pódio | 3 | 0,0711 | 0,0781 | 9,1 % [−2,1; 22,1] |
| Top 10 | 10 | 0,1224 | 0,1224 | 0 |

Os intervalos incluem zero: a melhora é provável, não demonstrada, com 24 corridas de teste. O próximo passo natural é um Plackett–Luce com fator de desconto por posição (modelo de Benter, 1994) em vez de truncamento.

### B.4 Limites

Três variáveis apenas; abandonos entram como posições; previsões de uma mesma corrida são dependentes (por isso a reamostragem é por corrida); a calibração da vitória depende muito de um piloto que venceu 28 das 46 corridas avaliadas.

---

## Parte C — #014: benchmark de voltas corrigido

### C.1 Dados

As mesmas 1.024 voltas limpas da fase 2 (uma sem tempo de setor, excluída: 1.023), com os três tempos de setor oficiais do OpenF1.

### C.2 Modelo

Para cada setor k, o modelo hierárquico de [`race_strategy/pace.py`](../../race_strategy/pace.py) com efeitos fixos (intercepto, duro − macio, degradação por composto, tendência por volta) e intercepto e degradação aleatórios por piloto. Aqui a verossimilhança é t de Student, ao contrário da fase 2: o objetivo é estimar o ritmo de cada piloto dentro da amostra, não prever voltas futuras, e a t é a que melhor descreve voltas com tráfego (curtose dos resíduos ≈ 15). Priors: σ(β₀) = 3 s, σ(β<sub>H</sub>) = 0,5 s, σ(degradação) = 0,2 s/volta, σ(γ) = 0,1 s/volta; half-Cauchy com escalas 0,5 s (intercepto) e 0,02 s/volta (inclinação). 4 cadeias × 2.000 sorteios após 1.000 de aquecimento; maior R̂ 1,001, menor ESS dos efeitos de piloto ≈ 4.100.

**Benchmark** de d no setor k: Δ<sub>d</sub><sup>k</sup> = u<sub>d</sub><sup>k</sup> + v<sub>d</sub><sup>k</sup>·10 − média do grid (pneu duro, 10 voltas de uso, volta 30). Volta: Σ<sub>k</sub> Δ<sub>d</sub><sup>k</sup>. Verificação: a soma reproduz o modelo ajustado à volta inteira com correlação 1,000, inclinação 0,999 e diferença máxima de 0,04 s.

### C.3 Resultados

| Piloto | Ritmo corrigido (s/volta, IC 90 %) | Posição (90 %) | Mediana bruta (s) |
|---|---|---|---|
| VER | −1,36 [−1,42; −1,31] | 1 | 95,53 |
| PER | −0,93 [−0,99; −0,88] | 2 | 96,22 |
| SAI | −0,80 [−0,85; −0,74] | 3 | 96,13 |
| LEC | −0,52 [−0,58; −0,46] | 4–6 | 96,76 |
| RUS | −0,52 [−0,58; −0,45] | 4–7 | 96,54 |
| NOR | −0,48 [−0,53; −0,42] | 4–7 | 96,57 |

Lista completa no JSON e na página. 15 dos 20 pilotos mudam de posição em relação à mediana bruta; τ de Kendall entre o ranking corrigido e a mediana 0,82, a melhor volta 0,64 e a volta ideal 0,69. A melhor volta e a volta ideal medem mais as condições (pneu novo, tanque vazio) que o piloto.

**Onde VER ganha**: dos 0,93 s sobre PER, 0,27 s vêm do setor 2; sobre SAI, 0,45 s de 0,80 s vêm do setor 2. O setor 2, o trecho sinuoso do meio da volta, concentra a maior parte da diferença de quase todo o grid.

**Efeitos comuns por setor** (média e IC 90 %):

| Efeito | S1 | S2 | S3 | Volta |
|---|---|---|---|---|
| Degradação do macio (s/volta) | 0,037 | 0,052 | 0,036 | 0,120 |
| Degradação do duro (s/volta) | 0,029 | 0,050 | 0,032 | 0,111 |
| Tendência por volta (s/volta) | −0,016 | −0,037 | −0,018 | −0,071 |
| Duro − macio, pneu novo (s) | +0,10 [0,06; 0,14] | −0,07 [−0,12; −0,01] | −0,04 [−0,07; −0,01] | −0,06 [−0,15; 0,03] |

O setor 2 tem a maior degradação e a maior tendência por volta. O sinal oposto de duro − macio entre o setor 1 e os setores 2 e 3 é pequeno, e o efeito do composto com pneu novo é pouco identificado nesta corrida (quase não há voltas de pneu novo em ritmo limpo); não é interpretado.

**Correlação dos resíduos na mesma volta** (IC 95 % de Fisher):

| Par | Todas as voltas (n = 1.023) | Peso pleno λ̄ > 0,5 em todos os setores (n = 727) |
|---|---|---|
| S1 × S2 | 0,23 [0,17; 0,29] | 0,02 [−0,06; 0,09] |
| S2 × S3 | 0,36 [0,31; 0,41] | 0,43 [0,37; 0,49] |
| S1 × S3 | 0,05 [−0,01; 0,11] | 0,03 [−0,05; 0,10] |

A correlação S1 × S2 vem das voltas com tráfego (some quando elas saem). A S2 × S3 permanece nas voltas limpas: alguma condição varia de volta para volta e afeta os dois setores juntos. Hipótese, não testada: estado térmico dos pneus traseiros, que dominam a tração nas saídas de curva dos dois setores. Consequência para o método: tratar os setores como independentes estreita um pouco o intervalo da soma.

### C.4 Limites

Uma corrida, pista seca; piloto e carro não se separam; ar sujo só entra pelo peso das voltas atípicas.

---

## Referências

- Bar-Shalom, Y., Li, X. R. e Kirubarajan, T. *Estimation with Applications to Tracking and Navigation*. Wiley, 2001.
- Julier, S. J. e Uhlmann, J. K. Unscented filtering and nonlinear estimation. *Proc. IEEE* 92(3), 2004.
- Van der Merwe, R. *Sigma-point Kalman filters for probabilistic inference in dynamic state-space models*. Tese, OGI, 2004.
- Pacejka, H. B. *Tyre and Vehicle Dynamics*, 3ª ed. Butterworth-Heinemann, 2012.
- Plackett, R. L. The analysis of permutations. *JRSS C* 24(2), 1975. Luce, R. D. *Individual Choice Behavior*. Wiley, 1959.
- Spiegelhalter, D. J. Probabilistic prediction in patient management and clinical trials. *Stat. Med.* 5, 1986.
- Gneiting, T. e Raftery, A. E. Strictly proper scoring rules, prediction, and estimation. *JASA* 102, 2007.
- Benter, W. Computer based horse race handicapping and wagering systems: a report. Em Hausch, Lo e Ziemba (orgs.), *Efficiency of Racetrack Betting Markets*. Academic Press, 1994.
- Gelman, A. et al. *Bayesian Data Analysis*, 3ª ed. CRC, 2013.
