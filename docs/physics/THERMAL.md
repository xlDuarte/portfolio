# Balanços térmicos e de massa: forno, usinagem e banho químico

Fase 5b do [plano científico](../PLANO-CIENTIFICO.md): projetos #029, #070, #090 e #069.

| Projeto | Base | Página |
|---|---|---|
| #029 Fornos e usinagem | Física com dados publicados (EN 1993-1-2, Churchill–Chu, Linden, VDI 3323, medições da ETH Zürich); forno, carga e torno hipotéticos | [/cases/029/](https://gabriel-automotive-industrial-lab.vercel.app/cases/029/) |
| #070 Insumos químicos | Balanço de massa e simulação de estoque; banho, titulações e demanda sintéticos | [/cases/timeseries/070/](https://gabriel-automotive-industrial-lab.vercel.app/cases/timeseries/070/) |
| #090 Custos e tarifa | Curva de carga real de siderúrgica (UCI 851) e tarifas reais da EDP SP (ANEEL, REH 3.541/2025) | [/cases/business/090/](https://gabriel-automotive-industrial-lab.vercel.app/cases/business/090/) |
| #069 Emissões | Tempo horário real de Taubaté (INMET A728, 2022–2025); chaminé hipotética | [/cases/timeseries/069/](https://gabriel-automotive-industrial-lab.vercel.app/cases/timeseries/069/) |

Código: [`thermal/`](../../thermal/). Dados do site: `python scripts/build_thermal_data.py` (≈ 2 min) → `site/data/thermal.json` e `python scripts/build_tariff_plume_data.py` (≈ 1,5 min) → `site/data/tariff_plume.json`, ambos determinísticos. Navegador: [`frontend/science/thermal.js`](../../frontend/science/thermal.js). Testes: `tests/test_thermal.py` e `tests/test_tariff_plume.py`.

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

## 4. #090 — modalidade, contrato e deslocamento de carga

**Dados.** Carga: 35.040 intervalos de 15 min de 2018 da DAEWOO Steel (Gwangyang, Coreia do Sul), UCI 851, CC BY 4.0; dois espelhos no GitHub com conteúdo idêntico após normalizar CRLF. O intervalo que termina à meia-noite vem datado com o dia que se encerra (NSM = 0) e foi movido para o dia seguinte. 960 MWh no ano, pico de 629 kW, fator de carga 17 %.

Tarifas: dados abertos da ANEEL, EDP SP, REH nº 3.541/2025 (vigência de 23/10/2025 a 22/10/2026), tarifa de aplicação A4. O servidor da ANEEL derruba a conexão TLS de IPs de data center, inclusive deste ambiente com o domínio liberado; os valores vêm de um espelho (diogoobs/tarifas-aneel, commit ceab633) que perdeu a vírgula decimal. A escala 1/100 é conferida contra o componente Fio B de um segundo espelho independente (lucascastro1412/monitor-tarifas-aneel, commit ed492eb), que precisa ser menor que a TUSD e é a maior parte dela.

| A4, EDP SP | Demanda ponta (R$/kW) | Demanda fora ponta (R$/kW) | Energia ponta (R$/MWh) | Energia fora ponta (R$/MWh) |
|---|---|---|---|---|
| Verde | 12.02 (única) | — | 1814.66 | 451.28 |
| Azul | 48.65 | 12.02 | 631.08 | 451.28 |

**Regras.** REN 1.000/2021: ponta de 3 h em dias úteis (17h30–20h30 na EDP SP, por fonte secundária), feriados nacionais fora da ponta, demanda faturada = max(contratada, medida), ultrapassagem acima de 5 % cobrada em dobro. Sem tributos nem bandeiras.

**Resultado.** Com o contrato ótimo (busca em grade; a tolerância torna o custo não convexo): Verde, 585 kW, R$ 719 mil/ano; Azul, 525/585 kW, R$ 863 mil/ano. A Verde ganha em todos os meses. O empate acontece quando cada kW de ponta é usado 41 h/mês (de 63 h de ponta); a planta usa de 17 a 33 h. Com a ponta das 18 h às 21 h, as conclusões não mudam (R$ 720 mil e R$ 863 mil).

**Deslocamento (PL).** Por mês, variáveis s_i (redução em cada intervalo de ponta, 0 ≤ s_i ≤ αL_i), u_j (aumento fora da ponta), D_p e D_fp; energia conservada dia a dia; objetivo = energia + demanda; HiGHS. Na Verde a economia é linear em α, R$ 1363 por MWh deslocado, porque a demanda fora da ponta não precisa subir: com α = 0,3, 43.8 MWh e R$ 60 mil/ano. Na Azul, mesmo com α = 0,5 o custo (R$ 692 mil) fica acima do da Verde.

## 5. #069 — pluma gaussiana com tempo horário real

**Tempo.** Arquivos horários anuais do INMET (BDMEP), baixados do portal oficial, estação A728 (Taubaté), 2022–2025: 35064 horas, 31829 válidas para vento, direção e temperatura. Radiação global em kJ/m² por hora (em branco à noite); a hora de cada registro é o fim do período, e o dia é definido pela elevação do Sol no meio da hora. Vento médio de 1.87 m/s, 29 % das horas abaixo de 1 m/s.

**Modelo.** Pluma gaussiana com reflexão no solo, σ_y e σ_z de Briggs (1973) para campo aberto, vento na altura da chaminé por lei de potência (expoentes rurais do ISC3), elevação de Briggs por empuxo (F_b ≈ 20 m⁴/s³ com o ar a 20 °C, para a chaminé hipotética de 40 m, Ø1,5 m, 12 m/s, 147 °C). Classe de Pasquill–Gifford pelo método de Turner; à noite, sem nebulosidade medida, duas hipóteses extremas. Receptores a cada 10° entre 100 m e 10 km; médias de 24 h só com ≥ 18 h válidas.

**Resultado (por g/s de MP10).** Máxima média anual de 0.397 µg/m³ a 662 m na direção 220°; pior média de 24 h de 1.67 µg/m³ a 588 m. As duas hipóteses noturnas dão máximas praticamente iguais, porque os máximos vêm do dia instável perto da fonte. Com os valores-guia da OMS de 2021 para MP10 (45 µg/m³ em 24 h, 15 µg/m³ no ano), que a CONAMA 506/2024 adota como padrão final, a emissão máxima sem concentração de fundo é 27 g/s, limitada pela média de 24 h.

**Limites.** Triagem: sem camada de mistura, relevo, edificações, deposição nem fundo. O Vale do Paraíba tem relevo e inversões térmicas que exigiriam AERMOD ou CALPUFF.

---

## Reprodução

    python scripts/build_thermal_data.py
    python scripts/build_tariff_plume_data.py
    python -m unittest tests.test_thermal tests.test_tariff_plume
