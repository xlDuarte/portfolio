# Ritmo, pneu e estratégia: método, verificação e validação

Fase 2 do [plano científico](../PLANO-CIENTIFICO.md). Código em [`race_strategy/`](../../race_strategy/) e [`vehicle_dynamics/tyre_energy.py`](../../vehicle_dynamics/tyre_energy.py). Navegador em [`frontend/strategy/`](../../frontend/strategy/). Página: [/cases/motorsport/101/](https://gabriel-automotive-industrial-lab.vercel.app/cases/motorsport/101/). Dados: `python scripts/build_strategy_data.py` (determinístico, cerca de 1 minuto), depois da fase 1.

## 1. Dados

GP do Bahrein 2024 (OpenF1, sessão 9472): 1.129 voltas cronometradas dos 20 pilotos. Ficaram 1.024 voltas limpas depois de excluir a volta 1, as voltas de entrada e saída de box e as voltas acima de 110 s. Dois compostos foram usados (macio e duro), e não houve safety car.

## 2. Modelo de ritmo

Modelo linear misto bayesiano. Efeitos fixos: intercepto, duro − macio, degradação por composto e tendência por volta. Cada piloto tem intercepto e inclinação de degradação aleatórios. A estimação usa Gibbs com condicionais conjugadas e priors half-Cauchy nas dispersões (representação de Wand et al., 2011). Foram ajustadas duas verossimilhanças: normal, e t de Student como mistura de escalas com ν numa grade.

**Escolha pela previsão, não pelo ajuste.** Validação temporal com ajuste nas voltas 2–42 (737 voltas) e previsão das voltas 43–57 (287 voltas):

| Modelo | CRPS (s) | Erro abs. médio (s) | Viés (s) | Cobertura 90 % | Cobertura 50 % |
|---|---|---|---|---|---|
| Bayesiano, erros normais (**usado**) | 0,272 | 0,370 | +0,116 | 90,9 % | 54,0 % |
| Bayesiano, erros t (ν ≈ 2,7) | 0,294 | 0,395 | +0,188 | 81,2 % | 33,4 % |
| Mínimos quadrados, efeito fixo de piloto | 0,267 | 0,362 | +0,116 | 89,9 % | — |
| Persistência (mediana das 5 últimas) | 0,612 | 0,827 | — | — | — |

A verossimilhança t descreve melhor o ritmo limpo: os resíduos de mínimos quadrados têm curtose ≈ 15 e assimetria ≈ 2, por causa do tráfego. Mesmo assim, ela prevê pior a corrida real, porque dá peso baixo justamente às voltas lentas que voltam a acontecer. O modelo normal fica calibrado (90,9 % numa banda de 90 %) e empata com mínimos quadrados em precisão. O ganho dele é carregar a incerteza dos parâmetros para a decisão. Todos os modelos têm viés positivo no fim da corrida: a tendência linear, extrapolada, promete mais evolução de pista do que houve. Uma alternativa quadrática na idade do pneu e outra na volta da corrida previram pior no mesmo protocolo (CRPS ≈ 0,29 e 0,32, num ajuste exploratório com 2 cadeias) e foram descartadas.

| Parâmetro (modelo normal) | Média | IC 90 % | R̂ | ESS |
|---|---|---|---|---|
| Duro − macio, mesma idade | +0,034 s | −0,079 a 0,148 | 1,000 | 8.000 |
| Degradação do macio | 0,129 s/volta | 0,118 a 0,141 | 1,000 | 8.000 |
| Degradação do duro | 0,111 s/volta | 0,105 a 0,117 | 1,000 | 7.431 |
| Tendência por volta | −0,071 s/volta | −0,073 a −0,069 | 1,001 | 8.000 |
| σ residual | 0,458 s | 0,441 a 0,475 | 1,000 | 7.296 |
| τ<sub>u</sub> (pilotos) | 0,701 s | 0,531 a 0,926 | 1,000 | 6.104 |
| τ<sub>v</sub> (degradação por piloto) | 0,006 s/volta | 0,001 a 0,013 | 1,038 | 189 |

τ<sub>v</sub> é o parâmetro de mistura mais lenta (ESS 189). A posterior dele se concentra perto de zero, então a diferença de degradação entre pilotos é pequena diante do ruído de uma corrida.

## 3. Combustível pela física

Os dados identificam só a tendência total γ = −0,071 s/volta. A física da fase 1 fornece ∂T/∂m = 23 ms/kg, a sensibilidade do tempo de volta à massa no simulador calibrado (incerteza de 15 % como hipótese). Multiplicada pelo consumo de 1,84 ± 0,10 kg/volta (hipótese), dá o efeito do combustível:

| Componente | s/volta | IC 90 % |
|---|---|---|
| Combustível | −0,042 | −0,053 a −0,031 |
| Evolução da pista (resto) | −0,029 | −0,040 a −0,018 |

## 4. Perda por parada

(Volta de entrada − ritmo previsto) + (volta de saída − ritmo previsto), para cada parada. A mediana das 40 paradas normais é **24,2 s** (IC 95 % por bootstrap de 23,9 a 24,6 s; interquartil de 23,7 a 24,8 s). Duas paradas acima de 40 s foram excluídas como problemas (SAR na volta 10 e BOT na volta 30). Para comparação, a mediana do tempo no pit lane registrado pelo OpenF1 é 24,8 s.

## 5. Decisão sob incerteza (planos fixos)

Custo de cada plano em forma fechada por stint. Intercepto, efeito do piloto e tendência se cancelam entre planos. Foram avaliados todos os planos legais (FIA, art. 30.5: dois compostos) de 1 a 3 paradas, stints de pelo menos 6 voltas e largada no macio usado das classificações (3 voltas), contra 1.200 sorteios da posterior e da perda por parada.

* Plano ótimo para VER: **macio–duro–duro, paradas nas voltas 15 e 36**, ótimo em 82 % dos sorteios. Arrependimento médio de 0,007 s.
* O plano real de VER (macio–duro–macio, 17/37) custa 3,1 s [1,7; 4,5] no modelo de ritmo isolado, que não vê tráfego, posição nem disponibilidade real de pneus.
* Largar de duro novo daria 6,1 s a menos **no modelo**. Isso não é recomendação: a volta 1 fica fora do ajuste.

## 6. Safety car: programação dinâmica estocástica

O estado é (volta, composto, idade, compostos usados, voltas restantes de safety car). A ação em cada volta é seguir ou parar para macio ou duro. O safety car começa com probabilidade p por volta verde e dura 4 voltas. Sob safety car, o custo da volta não depende do pneu, e a perda por parada é 50 % da perda em verde (hipótese). A equação de Bellman é resolvida de trás para frente. A política ótima foi avaliada por Monte Carlo (3.000 corridas) e comparada ao melhor plano fixo nas mesmas corridas:

| Safety cars esperados | Política adaptativa | Plano fixo | Valor da flexibilidade |
|---|---|---|---|
| 0 | 113,8 s | 113,8 s | 0,0 s |
| 0,56 | 108,6 s | 110,4 s | 1,9 s |
| 1,12 | 104,0 s | 107,4 s | 3,4 s |
| 1,96 | 96,9 s | 103,0 s | 6,1 s |

(Os tempos contam só a parte que depende da estratégia.) Sem safety car, a programação dinâmica reproduz exatamente o melhor plano fixo, o que serve de verificação.

## 7. Por que o pneu degrada

A volta calibrada da fase 1 dá carga e força por pneu (forças repartidas pela capacidade μ(F<sub>z</sub>)F<sub>z</sub> de cada pneu do eixo). A Magic Formula invertida dá a deriva α e o escorregamento κ. A potência de deslizamento é |F<sub>y</sub>|v|sin α| + |F<sub>x</sub>||κ|v.

* Energia por volta: dianteiro esquerdo 0,75, dianteiro direito 0,60, traseiro esquerdo 1,19 e traseiro direito 1,06 MJ. O eixo traseiro dissipa **63 %**, ou seja, o carro é limitado pela traseira no Bahrein [inferência do modelo].
* Deriva máxima de 7 a 8°, escorregamento máximo de 6 a 7 %, dentro da faixa de pico da curva assumida.
* Perda de aderência, da degradação medida dividida por |∂T/∂λ| = 39,2 s: macio 0,33 %/volta (0,091 %/MJ), duro 0,28 %/volta (0,078 %/MJ).
* Modelo térmico de dois nós por pneu: superfície e carcaça, com convecção, condução ao asfalto e histerese de rolagem. É verificado contra a solução analítica de regime permanente. Só a inclinação de convecção h₁ = 0,44 W/m²K por m/s foi ajustada, para a carcaça traseira estabilizar em 105 °C, uma hipótese. A temperatura não foi validada: não há medição pública.

## 8. Verificação automatizada

`tests/test_race_strategy.py` (11 testes):
* recuperação de parâmetros conhecidos em dados sintéticos com erros normais e t, com R̂ < 1,05;
* CRPS amostral contra a fórmula fechada da normal;
* custo de stint em forma fechada contra a soma direta;
* custo vetorizado igual ao direto;
* todos os planos com dois compostos;
* equivalência de planos;
* programação dinâmica sem safety car igual ao melhor plano;
* expectativa da programação dinâmica igual ao Monte Carlo;
* risco de safety car nunca piora a política adaptativa;
* regime permanente térmico igual à solução linear.

`frontend/strategy/sdp.test.mjs` (3 testes): a porta em JavaScript reproduz os valores esperados do Python para cada taxa de safety car.

## 9. Limites

Uma corrida, dois compostos, nenhum safety car observado. A degradação é linear na idade. O ritmo é isolado: sem tráfego, undercut, ar sujo, ordem de chegada ou jogos de pneu disponíveis por equipe. A largada no macio usado é imposta. Os parâmetros de safety car são cenário, e a temperatura do pneu não foi validada.
