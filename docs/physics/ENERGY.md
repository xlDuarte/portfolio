# Energia e clima com dados públicos: linha de base, pico de carga e galpão térmico

Fase 5a do [plano científico](../PLANO-CIENTIFICO.md). Projetos #008, #064 e #063.

| Projeto | Dados | Página |
|---|---|---|
| #008 Consumo de utilidades | Carga horária do subsistema SE/CO (ONS, 2019–2025) e temperatura de São Paulo, Rio e Belo Horizonte (INMET) | [/cases/008/](https://gabriel-automotive-industrial-lab.vercel.app/cases/008/) |
| #064 Demanda de energia em horário de ponta | Mesmos dados, pico diário | [/cases/timeseries/064/](https://gabriel-automotive-industrial-lab.vercel.app/cases/timeseries/064/) |
| #063 Impacto climático na planta | INMET Taubaté (A728) e São Paulo (A701); galpão hipotético | [/cases/timeseries/063/](https://gabriel-automotive-industrial-lab.vercel.app/cases/timeseries/063/) |

Código: [`energy/`](../../energy/). Dados do site: `python scripts/build_energy_data.py` (≈ 10 s, determinístico) → `site/data/energy.json`. Navegador: [`frontend/science/energy.js`](../../frontend/science/energy.js). Testes: `tests/test_energy.py`.

---

## 1. Procedência

Os portais do ONS e do INMET não são acessíveis a partir do ambiente de build. Os arquivos vêm de espelhos no GitHub, fixados por commit, e ficam versionados em gzip (≈ 5,8 MB no total) com o SHA-256 do texto original no manifesto, verificado por teste.

**ONS.** Curva de carga horária por subsistema (MWmed), anos 2019–2025, do espelho `byviniciusdep/previsao-carga-energia` (commit `f40dac4`). Conferência cruzada: o arquivo de 2025 tem o mesmo blob git (`ee3f68ac`) em `andredeomondes/monitor-carga-eletrica` (commit `744915b`), um repositório independente. A série do SE/CO tem 61.368 horas, sem lacunas. Manifesto: [`data/ons/manifest.json`](../../data/ons/manifest.json).

**INMET.** Exportação diária do BDMEP para quatro estações automáticas, do espelho `SousaLM/INMETdata` (commit `d1c9fbb`); os mesmos quatro arquivos têm blobs idênticos em `vin-greggio/inmet` (commit `18fe3a3`), que parece ser cópia da mesma exportação, então a conferência é de integridade, não de origem. Só as colunas marcadas (AUT) são usadas; as demais foram acrescentadas pelo autor do espelho. Latitude e altitude vêm do cabeçalho de cada arquivo. Linhas fisicamente impossíveis (mínima acima da média, média acima da máxima, valores fora de −10…45 °C) viram faltantes e são contadas no JSON: A701 27, A652 32, A521 2, A728 6. Manifesto: [`data/inmet/manifest.json`](../../data/inmet/manifest.json).

**Calendário.** Feriados nacionais com Páscoa pelo algoritmo anônimo gregoriano; Consciência Negra (20/11) a partir de 2024 (Lei 14.759/2023); Carnaval (segunda e terça) e Corpus Christi como pontos facultativos, porque derrubam a carga como feriados. Ponte: dia útil entre feriado e fim de semana.

---

## 2. #008 — linha de base por ponto de mudança (ASHRAE Guideline 14)

Para dias úteis (sem feriados, pontes e o confinamento de 16/03 a 30/06/2020), com T a média diária das três capitais:

    2P:  y = β₀ + β₁T
    3PC: y = β₀ + β₁(T − c)⁺          3PH: y = β₀ + β₁(c − T)⁺
    4P:  y = β₀ + β₁(T − c)⁻ + β₂(T − c)⁺
    5P:  y = β₀ + β₁(T − c₁)⁻ + β₂(T − c₂)⁺,   c₁ ≤ c₂

mais efeitos fixos de ano (crescimento da carga). Os pontos de mudança saem de busca em grade (0,1 °C entre 14 e 27 °C; no 5P, grade grossa e refinamento local) com β por mínimos quadrados; a forma é escolhida pelo BIC.

Métricas da Guideline 14: CV(RMSE) = √(SSE/(n − p)) / ȳ e NMBE = Σ(y − ŷ)/((n − p)ȳ). Com intercepto, NMBE é zero por construção. Resíduos de dias vizinhos são correlacionados; a Guideline corrige o tamanho de amostra para n′ = n(1 − ρ)/(1 + ρ), com ρ a autocorrelação de lag 1. Os intervalos de 95 % vêm de bootstrap em blocos móveis de 28 dias (300 réplicas, semente 8), que preserva a dependência.

**Resultado.** O 4P vence: ponto de equilíbrio 21,0 °C [20,3; 21,7], 0,51 GW/°C abaixo e 1,22 GW/°C [1,11; 1,36] acima, CV(RMSE) 3,7 %, ρ = 0,66, n′ ≈ 239 de 1.159 dias. Fins de semana: 21,1 °C e 1,11 GW/°C, com CV(RMSE) 5,9 %. Ajustes por ano variam mais que o intervalo conjunto porque, num ano só, ponto de mudança e inclinação são pouco identificados (poucos dias quentes).

**Limites.** Três capitais aproximam o clima de um subsistema continental; umidade e radiação não entram; a regressão é associação, não efeito causal isolado da temperatura.

---

## 3. #064 — pico diário um dia à frente

    y_t = Σ_d δ_d·1[dow=d] + γ_h·feriado + γ_p·ponte + Σ_{k=1..3}[a_k sin(2πk·doy/365,25) + b_k cos(…)] + τ·t
          + β₁(T_t − T_b)⁻ + β₂(T_t − T_b)⁺ + u_t,     u_t = φu_{t−1} + e_t

T_b vem de um 4P nos dias úteis de treino; β por MQO; φ dos resíduos de treino. Previsão de um dia à frente usa o resíduo observado de ontem. Conjunto de 2.000 trajetórias por reamostragem das inovações empíricas e_t do treino. Com temperatura prevista T̂ de erro σ, cada trajetória sorteia T ~ N(T̂, σ²) antes da dobradiça (não linear), o que alarga a faixa onde a carga é sensível à temperatura.

Treino: 2019–2022 sem o confinamento (1.354 dias). Teste: 2023-01-01 a 2023-11-30 (334 dias; o conjunto do INMET termina aí). Escores: erro percentual médio, RMSE, CRPS pela identidade da amostra ordenada (CRPS = E|X − y| − ½E|X − X′|) e cobertura da faixa de 90 %.

| Previsão | Erro % | CRPS (MW) | Cobertura 90 % |
|---|---|---|---|
| Temperatura observada (oráculo) | 1,66 | 615 | 85 % |
| Sem temperatura | 1,82 | 685 | 84 % |
| Erro de 1 °C, valor direto | 1,92 | 713 | 80 % |
| Erro de 1 °C, incerteza propagada | 1,95 | 679 | 90 % |
| Erro de 2 °C, valor direto | 3,03 | 1.202 | 62 % |
| Erro de 2 °C, incerteza propagada | 3,12 | 1.062 | 89 % |
| Mesmo dia da semana anterior | 3,91 | — | — |

**Leitura.** A temperatura observada reduz o erro de 1,82 % para 1,66 %, mas esse é o teto: com 1 °C de erro de previsão o ganho desaparece, porque o termo autorregressivo (φ ≈ 0,67) já carrega o tempo de ontem. Usar a temperatura prevista como certa estreita demais a faixa; propagar a incerteza devolve a cobertura nominal. O erro de temperatura é simulado (gaussiano, semente fixa), não medido de um modelo numérico real. Uma única divisão temporal: diferenças entre linhas não têm teste formal (por exemplo Diebold–Mariano).

**Hora do pico.** A maior parte dos picos do SE/CO cai entre 18 h e 20 h; a fração de dias com pico entre 12 h e 16 h vai de 36,7 % (2019) a 4,9 % (2022) e oscila depois. Geração distribuída, verões diferentes e mudança de contabilização no ONS são hipóteses não testadas.

---

## 4. #063 — clima de Taubaté e galpão 1R1C

**Forçante horária.** Temperatura por duas meias-cossenoides: da mínima no nascer do sol até a máxima às 15 h, e de volta até a mínima do dia seguinte. Radiação global diária por Hargreaves–Samani, R_s = k_Rs √(T_max − T_min) R_a, com k_Rs = 0,16 (interior) e R_a da FAO-56 (eq. 21; teste reproduz o exemplo 8 da FAO-56, 32,2 MJ m⁻² dia⁻¹ a 20° S em 3 de setembro), distribuída por um seno entre nascer e pôr do sol. Lacunas internas de anos simulados preenchidas pela climatologia do dia do ano.

**Galpão.** Uma capacitância C (100 kJ/m²K × 2.000 m²) ligada ao ar externo pelas paredes (U = 2,5 W/m²K, 1.440 m²) e pela ventilação (0,5 renovação/h, 16.000 m³), e à temperatura sol-ar T_sa = T + αG/h_e (h_e = 17 W/m²K) pelo telhado:

    C dT_i/dt = U_r A_r (T_sa − T_i) + (U_w A_w + ṁc_p)(T − T_i) + q_int − Q_c

Euler implícito com passo de 1 h (incondicionalmente estável); resfriamento ideal que mantém T_i ≤ 26 °C; energia elétrica Q_c/COP com COP 3. Cenários: telha metálica (U_r = 5) ou sanduíche (U_r = 0,5), escura (α = 0,8) ou branca (α = 0,3). Teste confere o regime permanente contra a solução analítica.

**Resultado (média dos 7 anos completos).** Resfriamento: 236,5 / 90,3 / 24,6 / 15,9 MWh/ano (metálica escura, metálica branca, sanduíche escura, sanduíche branca). R² entre resfriamento anual e graus-dia de resfriamento (base 18 °C): 0,55–0,63, porque a radiação no telhado, que domina, não está nos graus-dia.

**Tendência.** Mann–Kendall (variância corrigida para empates) e inclinação de Sen com IC de Gilbert. Taubaté tem 7 anos com ≥ 330 dias válidos; São Paulo, 16. Nenhuma tendência significativa em temperatura média, graus-dia ou dias ≥ 32 °C. Com séries tão curtas o teste não tem poder para tendências de décimos de grau por década; o resultado é "não mensurável com estes dados", não "inexistente".

**Limites.** Temperatura interna sem refrigeração é limite superior (ventilação natural real é maior; sem estratificação). A forçante horária é reconstruída de valores diários, não medida. Galpão hipotético: compara coberturas, não descreve um prédio.

---

## 5. Reprodução

    python scripts/build_energy_data.py
    python -m unittest tests.test_energy

Versões de Python, NumPy, SciPy e pandas ficam gravadas em `site/data/energy.json`.
