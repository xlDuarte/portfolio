# Balanços térmicos e de massa: forno, usinagem e banho químico

Fase 5b do [plano científico](../PLANO-CIENTIFICO.md), primeira parte: projetos #029 e #070. Os projetos #090 (tarifa horossazonal) e #069 (pluma gaussiana) dependem de dados oficiais da ANEEL e do INMET que o ambiente de build ainda não alcança.

| Projeto | Base | Página |
|---|---|---|
| #029 Fornos e usinagem | Física com dados publicados (EN 1993-1-2, Churchill–Chu, Linden, VDI 3323, medições da ETH Zürich); forno, carga e torno hipotéticos | [/cases/029/](https://gabriel-automotive-industrial-lab.vercel.app/cases/029/) |
| #070 Insumos químicos | Balanço de massa e simulação de estoque; banho, titulações e demanda sintéticos | [/cases/timeseries/070/](https://gabriel-automotive-industrial-lab.vercel.app/cases/timeseries/070/) |

Código: [`thermal/`](../../thermal/). Dados do site: `python scripts/build_thermal_data.py` (≈ 2 min, determinístico) → `site/data/thermal.json`. Navegador: [`frontend/science/thermal.js`](../../frontend/science/thermal.js). Testes: `tests/test_thermal.py`.

---

## 1. #029 — forno elétrico de tratamento térmico

**Paredes.** Condução 1D em regime permanente por três camadas com condutividade linear na temperatura, k = k₀ + k₁T. Para uma camada, q·L = ∫k dT é exato, então a face fria sai de uma equação do segundo grau dado o fluxo. A carcaça perde calor por convecção natural e radiação:

    q = h_c(T_s)(T_s − T_∞) + εσ(T_s⁴ − T_∞⁴)

com Churchill e Chu (1975) nas faces verticais, Nu = 0,54 Ra^¼ / 0,15 Ra^⅓ no teto (placa aquecida voltada para cima) e Nu = 0,52 Ra^⅕ na base suspensa (voltada para baixo), propriedades do ar pela lei de Sutherland à temperatura de filme. O fluxo é a raiz do resíduo (Brent), com o limite superior obtido por bissecção para manter a carcaça acima do ambiente.

| Camada (hipotética) | Espessura | k₀ (W/m·K) | k₁ (W/m·K²) | ρ (kg/m³) | Limite (°C) |
|---|---|---|---|---|---|
| Tijolo isolante classe 26 | 230 mm | 0,17 | 1,3·10⁻⁴ | 800 | 1.430 |
| Placa de silicato de cálcio | 100 mm | 0,05 | 1,0·10⁻⁴ | 250 | 1.000 |
| Carcaça de aço | 6 mm | 45 | 0 | 7.850 | — |

Resultado a 860 °C: 374 W/m², carcaça a 57–70 °C, interface tijolo/placa a 530 °C (abaixo do limite de 1.000 °C da placa), 5,2 kW no total para 14,1 m² de área média.

**Porta aberta.** Radiação de cavidade pela abertura de 0,8 × 0,7 m numa parede de 336 mm. Com batentes rerradiantes, o fator de troca é (1 + F₁₂)/2, onde F₁₂ é o fator de forma entre as duas faces da abertura (retângulos paralelos alinhados, Incropera tabela 13.2; o teste confere F₁₂ = 0,1998 para quadrados à distância do lado). Troca de ar: V̇ = (C_d W/3)·√(g′H³), g′ = gΔρ/ρ̄ (Linden, 1999). Se o ar saísse a 860 °C, seriam 315 kW, mais que os 120 kW instalados. O modelo trata o gás da câmara como bem misturado e aquecido pelo revestimento com h_in A_in, o que resolve T_g ≈ 281 °C e 69 kW enquanto a porta está aberta, mais a purga do gás quente a cada abertura. A extrapolação de Boussinesq a 835 K de diferença é declarada como ordem de grandeza.

**Carga.** 500 kg de barras de aço Ø80 mm, condução radial por diferenças finitas implícitas (21 nós, Δt = 10 s), calor específico e condutividade do aço carbono pela EN 1993-1-2, eq. 3.2 e 3.3, com o pico de 5.000 J/kg·K em 735 °C. Contorno: εF_exp σ(T_c⁴ − T_s⁴) + h(T_c − T_s), ε = 0,7, F_exp = 0,6, h = 10 W/m²K. Enquanto a potência pedida passa dos 120 kW, a temperatura da câmara é a raiz do balanço P_max = Q_carga(T_c) + Q_paredes(T_c).

| Ciclo | Valor |
|---|---|
| Núcleo a 850 °C | 1,46 h |
| Ciclo com encharque de 30 min e porta | 2,00 h |
| Tempo limitado pela potência | 17 min |
| Energia: carga / paredes / porta (radiação) / porta (ar) | 83,7 / 10,1 / 1,9 / 3,7 kWh |
| Total, energia por tonelada, fração útil | 99,3 kWh, 199 kWh/t, 84 % |
| Fechamento do balanço | −0,10 % |

A entalpia da carga pela integral da norma (83,69 kWh) confere com a energia acumulada pelo esquema numérico.

**Incerteza.** Monte Carlo com 400 sorteios uniformes: k das duas camadas ×0,8–1,2, emissividade da carcaça 0,80–0,95 e da carga 0,60–0,85, exposição 0,45–0,75, C_d 0,5–0,7, tempo de porta aberta 120–300 s, h_in 8–25 W/m²K. Faixa de 90 %: 193 a 208 kWh/t. Coeficientes de regressão padronizados nos postos (Saltelli et al., 2004) apontam o tempo de porta aberta e o h_in como dominantes; a exposição da carga reduz a energia (ciclo mais curto, menos perda de parede).

**Parada de fim de semana.** Condução transitória no revestimento (implícita, propriedades defasadas um passo), por m² de uma face vertical, vezes a área média. Opção A mantém 860 °C. Opção B desliga com a câmara fechada (face quente adiabática), reaquece a 150 K/h e fica pronta quando a face quente está no ponto de ajuste e o revestimento absorve no máximo 1,5 vez a perda de regime; o tempo desligado é o maior possível para ficar pronto no fim da parada (bissecção). As duas opções são integradas até 72 h depois da parada. Economia: 8, 22, 62 e 98 kWh para paradas de 12, 24, 48 e 64 h, contra 63, 126, 252 e 336 kWh que manter quente gasta durante a própria parada (13 % a 29 %): a massa térmica do tijolo devolve à conta a maior parte do que se deixou de gastar desligado.

## 2. #029 — energia de corte

Kienzle: F_c = k_c1.1 · b · h^(1−m_c), com b = a_p/sen κ e h = f·sen κ. A energia específica do cavaco é u = k_c1.1 · h^(−m_c), em N/mm² ≡ mJ/mm³. Gutowski et al. (2006): P = P₀ + k·ṽ, ou seja, e = P₀/ṽ + u/η por volume removido. Torno hipotético com P₀ = 4 kW e η = 0,8.

Coeficientes: tabela VDI 3323 do guia técnico da ISCAR (aço carbono ≥ 0,25 % C recozido: k_c1 = 1.500 N/mm², m_c = 0,22) e as 11 medições de Ck45 (671 MPa) de Klippel et al. (ETH Zürich, 2022, arXiv:2209.04197, tabela C.17), uma por velocidade de corte ensaiada: k_c1.1 de 1.368 a 1.935 N/mm², m_c de 0,17 a 0,51. A correspondência exata entre cada coluna e a velocidade não foi extraída com segurança do PDF, por isso as medições entram como dispersão, não como função da velocidade. O catálogo fica abaixo de 9 das 11 medições.

Passe de Ø80 para Ø70 mm em 1 m (v_c = 200 m/min, f = 0,25 mm): F_c = 2.546 N, P_c = 8,5 kW, 4,7 min, 1,15 kWh (3,5 J/mm³, dos quais 2,0 no cavaco). O tratamento térmico do mesmo metro de barra consome 7,8 kWh, 6,8 vezes mais.

## 3. #070 — banho químico e reposição

    V dC/dt = −k_d V C − q C − r a(t) + adições

Decomposição de primeira ordem k_d, arraste q (L/h, proporcional a C), reação r (g/m², independente de C) sobre a área tratada a(t). Entre adições, C(t) = C* + (C₀ − C*)e^(−λt), com λ = k_d + q/V e C* = −r a/(Vλ). Simulação exata hora a hora; adição até 30 g/L quando passa de 26 g/L.

**Identificabilidade.** Titulações sintéticas a cada 4 h, desvio de 0,25 g/L, quatro semanas, ajuste por mínimos quadrados limitados sobre a solução exata:

| Desenho | k_d (1/h) | q (L/h) | r (g/m²) | corr(q, r) |
|---|---|---|---|---|
| Verdade | 0,0040 | 6,00 | 1,20 | — |
| Uma faixa, com fins de semana | 0,0040 ± 0,00004 | 8,69 ± 2,55 | 0,00 ± 1,17 | −0,998 |
| Uma faixa, só dias de produção | 0,0041 ± 0,00006 | 4,85 ± 3,54 | 1,54 ± 1,60 | −0,998 |
| Duas faixas (26–30 e 18–22 g/L) | 0,0040 ± 0,00004 | 5,94 ± 0,33 | 1,22 ± 0,13 | −0,841 |

Dentro de 26–30 g/L, qC é quase constante e se confunde com r·a. O consumo total por dia útil continua preciso (IC 95 % de 28,40 a 28,48 kg de concentrado; verdade 28,42 kg). Mudar a faixa de trabalho por uma semana separa os mecanismos.

**Reposição.** Demanda diária de 20,3 kg (desvio 4,4 kg, zero nos fins de semana), prazo do fornecedor de 4, 5, 7 ou 10 dias (média 5,4, variância 3,64 dias²), custos de R$ 350 por pedido, R$ 0,06 por kg·dia e R$ 25 mil por dia de linha parada, 20 anos simulados:

| Política | s | S | Serviço por ciclo | Dias sem concentrado/ano | Custo anual |
|---|---|---|---|---|---|
| Clássica, prazo fixo | 133 | 620 | 86,4 % | 4,8 | R$ 131.202 |
| Clássica com Var[L] | 203 | 689 | 98,3 % | 0,25 | R$ 18.990 |
| Ótimo da simulação | 193 | 609 | 100 % | 0 | R$ 12.676 |

A regra clássica com σ_L² = E[L]σ_d² + μ_d²Var[L] chega perto do ótimo; ignorar a variância do prazo é o erro caro.

---

## Reprodução

    python scripts/build_thermal_data.py
    python -m unittest tests.test_thermal
