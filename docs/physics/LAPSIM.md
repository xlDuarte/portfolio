# Simulador de volta: método, verificação e validação

Fase 1 do [plano científico](../PLANO-CIENTIFICO.md). Código em [`vehicle_dynamics/`](../../vehicle_dynamics/) (Python) e [`frontend/lapsim/`](../../frontend/lapsim/) (navegador). A ferramenta está em [/motorsport/lap-simulator/](https://gabriel-automotive-industrial-lab.vercel.app/motorsport/lap-simulator/). Os dados são gerados por `python scripts/build_lapsim_data.py` (determinístico, cerca de 3 minutos).

## 1. Dados

| Item | Valor | Origem |
|---|---|---|
| Sessão | GP do Bahrein 2024, corrida, `session_key` 9472 | OpenF1, já no repositório (`site/motorsport/data/bahrain-2024-race.json`) |
| Janela | 15:05:30–15:09:30 UTC, VER, PER, SAI | idem |
| Posições | 2.883 amostras, decímetros, ~4 Hz | OpenF1 `location` |
| Velocidade | 356 amostras na volta 3 de VER, km/h, ~4 Hz | OpenF1 `car_data` |
| Voltas completas na janela | volta 3 de cada piloto (VER 96,753 s, PER 97,297 s, SAI 97,080 s) | OpenF1 `laps` |
| Ar | 18,9 °C, 1017,1 hPa, 46 % UR → ρ = 1,209 kg/m³ | OpenF1 `weather`, mistura de gases ideais com pressão de saturação de Tetens |

**Achado:** as posições dos três carros coincidem entre si com **4 cm de RMS** lateral. Logo, o OpenF1 publica posições projetadas num mapa do traçado, não GPS bruto. A trajetória individual de cada piloto não é observável nesses dados.

## 2. Modelo

| Bloco | Equação ou método | Referência |
|---|---|---|
| Traçado | Série de Fourier periódica (160 harmônicos) com penalidade ∫x″², λ por validação cruzada generalizada; curvatura analítica; giro total verificado = −360,000° | Craven & Wahba (1979) |
| Trajetória | Curvatura mínima com ±4,5 m em torno do mapa, curvatura linearizada κ + n″ + κ²n, L-BFGS-B com limites | Braghin et al. (2008); Heilmeier et al. (2020) |
| Pneu | Magic Formula pura, estrutura MF 6.1 (carga e pressão); escalas λ<sub>μy</sub> e λ<sub>μx</sub> | Pacejka (2012), cap. 4 |
| Carro | Arrasto e downforce quadráticos, transferência longitudinal e lateral por eixo, guinada em regime, elipse de atrito por eixo, potência nas rodas, balanço de freio fixo | Milliken & Milliken (1995) |
| Envelope | g-g-V por bisseção, tabelado em (v, a<sub>y</sub>/a<sub>y,máx</sub>) e interpolado bilinearmente | — |
| Volta | Velocidade-limite de curva, passagens de aceleração e frenagem em d(v²)/ds pelo método de Heun, com a elevação | Brayshaw & Harrison (2005) |
| Calibração | MAP: velocidades + tempo oficial da volta + priors gaussianos; mínimos quadrados não lineares (TRF); covariância de Laplace com tamanho efetivo de amostra AR(1) | — |

## 3. Verificação (o código resolve as equações certas)

`tests/test_vehicle_dynamics.py` traz 21 testes contra resultados fechados: derivada da Magic Formula na origem igual à rigidez de deriva, pico igual a μF<sub>z</sub>, simetria ímpar, sensibilidade de carga, densidade do ar ISA (1,225 kg/m³), conservação de carga com downforce, transferência longitudinal, skidpad em μg, aceleração limitada por potência P/(mv), frenagem limitada pelo eixo dianteiro (a = μg(b/ℓ)/(β − μh/ℓ)), rampa g·sin θ, velocidade máxima P = ½ρC<sub>D</sub>Av³, curvatura e comprimento de um círculo, derivada de Fourier, raio recuperado de amostras com ruído, curvatura mínima respeitando limites, volta num círculo em 2πR/√(μgR), monotonicidade em aderência e massa, tabela do envelope contra solução direta e recuperação de parâmetros conhecidos (todos a menos de 3 erros-padrão) num traçado sintético.

`frontend/lapsim/model.test.mjs` traz 5 testes. A porta em JavaScript reproduz o Python no mesmo carro e na mesma pista: tempo 96,7485 s contra 96,748 s, diferença máxima de **0,014 km/h** no perfil de velocidade.

Convergência no passo Δs (Heun, segunda ordem): 96,647 s (8 m), 96,748 s (4 m), 96,788 s (2 m), 96,791 s (1 m), 96,794 s (0,5 m); extrapolação de Richardson 96,795 s. O ajuste usa 2 m, com erro de discretização de cerca de 7 ms.

## 4. Calibração (volta 3 de VER)

| Parâmetro | Estimativa ± EP | Prior | Leitura |
|---|---|---|---|
| λ<sub>μy</sub> | 1,018 ± 0,084 | 1,0 ± 0,3 | aderência lateral usada, próxima da curva assumida |
| λ<sub>μx</sub> | 0,721 ± 0,054 | 1,0 ± 0,3 | frenagem e tração abaixo do limite: volta de corrida, gestão de pneu, amostragem de 4 Hz |
| C<sub>L</sub>·A | 3,72 ± 0,88 m² | 4,0 ± 1,5 | correlação −0,89 com λ<sub>μy</sub>: a velocidade não separa os dois |
| C<sub>D</sub>·A | 1,63 ± 0,19 m² | 1,2 ± 0,4 | correlação 0,81 com P |
| P (rodas) | 595 ± 42 kW | 620 ± 50 kW | prior informativo, porque a reta só identifica P/C<sub>D</sub>A |

Ajuste: RMSE 10,2 km/h, R² 0,975, viés +1,8 km/h, volta 96,788 s contra 96,753 s medidos. A autocorrelação lag-1 dos resíduos é 0,887, o que dá cerca de 21 amostras independentes efetivas em 356. Os erros-padrão já incluem essa correção.

## 5. Validação fora da amostra

Com os parâmetros de VER fixos, o erro de velocidade nas outras oito voltas observadas ficou entre 9,7 e 15,2 km/h de RMSE. A pior é a volta 4 de PER, só parcialmente na janela. As calibrações independentes de PER e SAI estão na página. A diferença de C<sub>L</sub>·A e C<sub>D</sub>·A entre carros mistura efeito de carro com ar sujo. O modelo não separa os dois.

## 6. Incerteza e sensibilidade

* Monte Carlo (200 sorteios da posterior de Laplace, semente 110): 97,24 ± 0,58 s, IC 95 % de 96,55 a 99,08 s. A cauda direita é longa porque o tempo de volta é convexo nos parâmetros.
* Sensibilidade local (diferença central, s por +1 %): λ<sub>μy</sub> −0,256, massa +0,204 (0,23 s por 10 kg), λ<sub>μx</sub> −0,139, P −0,107, C<sub>L</sub>·A −0,096, C<sub>D</sub>·A +0,076, altura do CG +0,027, balanço aero +0,025.
* Largura útil (hipótese): o tempo de volta é 97,04 s com ±3,0 m, 96,79 s com ±4,5 m e 96,61 s com ±6,0 m. Com o mapa do OpenF1 sem otimizar, a volta sai em 100,85 s, quatro segundos mais lenta. Num ajuste preliminar feito direto sobre o mapa, λ<sub>μy</sub> foi a 1,33: o raio de curva subestimado vira aderência inexistente. Por isso a trajetória é reconstruída antes da calibração.

## 7. Limites

Não modelados: temperatura e desgaste do pneu, gestão de energia do ERS (potência constante), DRS, ar sujo, cinemática de suspensão, câmber, inércia de guinada (regime permanente), forma real da curva do pneu (só a escala é identificada), trajetória individual (mapa projetado). Os parâmetros fixos (massa com combustível estimado, CG, bitolas, distribuição de rigidez à rolagem, balanço de freio) são hipóteses de ordem de grandeza.
