# Rolamentos com vibração real: diagnóstico por envelope, detecção de anomalias e assinaturas

Fase 4a do [plano científico](../PLANO-CIENTIFICO.md). Projetos #004, #104 e #052, todos sobre os mesmos 40 registros reais do banco de rolamentos da Case Western Reserve University (CWRU).

| Projeto | Pergunta | Página |
|---|---|---|
| #004 Espectro NVH | Qual defeito existe, pela física do rolamento? | [/cases/004/](https://gabriel-automotive-industrial-lab.vercel.app/cases/004/) |
| #104 Anomalias em vibração | O que um detector e um classificador aprendem, e como validá-los? | [/cases/motorsport/104/](https://gabriel-automotive-industrial-lab.vercel.app/cases/motorsport/104/) |
| #052 Assinaturas de diagnóstico | Uma biblioteca de defeitos funciona em outra velocidade e outra peça? | [/cases/recommendation/052/](https://gabriel-automotive-industrial-lab.vercel.app/cases/recommendation/052/) |

Código: [`bearings/`](../../bearings/). Dados: `python scripts/fetch_cwru.py` e depois `python scripts/build_bearing_data.py` (≈ 30 s), que escreve `site/data/bearings-cwru.json`. Navegador: [`frontend/science/bearings.js`](../../frontend/science/bearings.js).

---

## 1. Dados e procedência

- **Fonte canônica:** CWRU Bearing Data Center. O site da universidade não é acessível a partir do ambiente de build; os arquivos vêm do espelho público `s-whynot/CWRU-dataset` no commit `0d07cb1`, que preserva os nomes e números originais.
- **Integridade:** [`data/cwru/manifest.json`](../../data/cwru/manifest.json) guarda o SHA-256 de cada arquivo `.mat`; `fetch_cwru.py` recusa qualquer divergência. Só o canal do acelerômetro do lado do acionamento é guardado (`data/external/cwru/`, fora do git). Um trecho de 2 s de quatro registros fica em `tests/fixtures/cwru_excerpt.npz` para os testes.
- **Subconjunto:** 12 kHz, lado do acionamento: saudável (97–100), pista interna, esfera e pista externa na posição de 6 h, com defeitos de 0,007″, 0,014″ e 0,021″, cada um a 0, 1, 2 e 3 hp. 4 + 36 = 40 registros.
- **Problemas encontrados nos dados:**
  1. O arquivo do registro 99 guarda também as variáveis do registro 98. A primeira versão do manifesto pegou a variável errada e os dois registros saíram idênticos; corrigido usando a variável com o número do próprio registro.
  2. Os registros 98 e 99 não têm rotação gravada; usa-se a nominal da carga (1.772 e 1.750 rpm).
  3. Taxa de amostragem dos saudáveis: lido a 12 kHz, o registro 97 mostra a linha de 1× rotação 37,7 dB acima do fundo local; lido a 48 kHz, 17,1 dB. O registro é de 12 kHz, como os de falha.

Rolamento: SKF 6205-2RS JEM, 9 esferas, d = 7,94 mm, D = 39,04 mm, φ = 0. Ordens calculadas: BPFO 3,5848; BPFI 5,4152; FTF 0,3983; 2·BSF 4,7134 (CWRU publica 3,5848; 5,4152; 0,39828; 4,7135).

## 2. #004 — diagnóstico por envelope

**Cadeia.** Janelas de 1 s. Caminho A: pré-branqueamento cepstral, y = IFFT(X/|X|) (Randall e Sawalhi, 2011). Caminho B: passa-faixa Butterworth de 4ª ordem, fase zero, na banda de maior curtose espectral por STFT (Antoni, 2006), com janelas de 16, 24 e 32 amostras (largura de banda 1.500, 1.000 e 750 Hz, sempre mais de quatro vezes BPFI). Nos dois: espectro do quadrado do envelope (Hilbert).

**Indicador.** Para cada tipo de defeito, média dos três primeiros harmônicos de 10·log₁₀(pico/mediana local), com o pico procurado em ±1,5 % da frequência teórica (escorregamento) e a mediana em ±12 Hz excluindo a janela de busca.

**Decisão sem rótulos.** Tipo de maior indicador, se acima de τ = percentil 99 do maior indicador nas janelas saudáveis. Nas janelas saudáveis avaliadas, τ vem das outras três cargas.

**Resultado** (500 janelas):

| Real \ previsto (caminho A) | Normal | Pista externa | Pista interna | Esfera |
|---|---|---|---|---|
| Normal | 138 | 0 | 1 | 1 |
| Pista externa | 40 | 80 | 0 | 0 |
| Pista interna | 0 | 0 | 120 | 0 |
| Esfera | 114 | 1 | 3 | 2 |

Acurácia balanceada 66,7 % (caminho A) e 66,5 % (caminho B); τ = 4,68 e 5,43 dB. Por registro (maioria das janelas): pista interna 12/12, pista externa 8/12 (os quatro de 0,014″ falham), esfera 0/12. Os defeitos de esfera não deixam pente em 2·BSF, BSF nem nas bandas laterais da gaiola; isso concorda com o estudo de referência de Smith e Randall (MSSP 64–65, 2015), em que os defeitos de esfera são a categoria menos diagnosticável.

**Verificação com verdade conhecida** (`bearings/simulate.py`, modelo de Randall e Antoni, 2011): impactos em BPFO ou BPFI com 1 % de variação aleatória do período, ressonância de 3,5 kHz com ζ = 0,05, modulação pela zona de carga na pista interna, harmônicos da rotação, ruído branco. Limiar de 1 % de falso alarme por 200 simulações sem defeito; 60 simulações por ponto. SNR = 20·log₁₀(amplitude do impacto/σ do ruído).

| P(detecção), pista externa | 0 dB | 3 dB | 6 dB | 9 dB | 12 dB |
|---|---|---|---|---|---|
| Ruído branco, sem processamento | 0,00 | 0,45 | 1,00 | 1,00 | 1,00 |
| Ruído branco, pré-branqueamento | 0,02 | 0,13 | 0,87 | 1,00 | 1,00 |
| Ruído branco, banda da curtose | 0,05 | 0,62 | 1,00 | 1,00 | 1,00 |
| Engrenamento forte, sem processamento | 0,00 | 0,00 | 0,00 | 0,10 | 0,98 |
| Engrenamento forte, pré-branqueamento | 0,00 | 0,18 | 0,78 | 1,00 | 1,00 |
| Engrenamento forte, banda da curtose | 0,00 | 0,00 | 0,00 | 0,27 | 1,00 |

Sem componentes discretos, a banda da curtose é a melhor e o pré-branqueamento perde um pouco (também achata a ressonância). Com engrenamento forte (27 dentes, seis harmônicos), só o pré-branqueamento detecta abaixo de 12 dB. A pista interna exige mais SNR nos dois cenários, pela modulação.

## 3. #104 — detecção de anomalias e protocolos de validação

**Atributos.** Físicos (8): log RMS, log curtose, log fator de crista, assimetria, os três indicadores de envelope e log(1 + curtose espectral máxima). Espectrais (32): log da potência média em 32 bandas iguais de 0 a 6 kHz (Welch, 1.024 amostras).

**Detector.** Distância de Mahalanobis ao saudável, com covariância encolhida por Ledoit–Wolf. Treino no saudável de três cargas; teste no saudável da quarta e em todas as falhas dessa carga.

| Atributos | AUC pista interna | AUC esfera | AUC pista externa | Falso alarme 0/1/2/3 hp |
|---|---|---|---|---|
| Físicos | 1,000 | 1,000 | 0,990 [0,945; 1,000] | 100 / 8 / 8 / 3 % |
| Espectrais | 1,000 | 1,000 | 1,000 | 100 / 100 / 100 / 100 % |

A AUC perto de 1 não significa detector pronto. O saudável a 0 hp vibra mais (RMS 0,073 g contra 0,063–0,065 g nas outras cargas), e um detector treinado em 1–3 hp marca todas as janelas dele. Com atributos espectrais, o limiar não serve em nenhuma carga. As falhas pontuam ainda mais alto, então a ordem dos escores (AUC) fica perfeita enquanto o limiar falha. Intervalos por reamostragem de registros inteiros; com só quatro registros saudáveis, são otimistas.

**Classificação (4 classes, regressão logística multinomial L2):**

| Protocolo | Espectrais | Físicos |
|---|---|---|
| Janelas sorteadas 70/30 | 100,0 % | 89,9 % |
| Deixa uma carga de fora | 99,4 % | 88,7 % |
| Deixa um tamanho de defeito de fora (rolamento novo) | 60,6 % | 73,7 % |
| Regra física de envelope, sem treino | 66,7 % | |

Sortear janelas mede a memória da gravação. Deixar uma carga de fora mantém o mesmo rolamento. Só o protocolo por tamanho põe uma peça fisicamente diferente no teste; os atributos físicos generalizam melhor (Hendriks, Dumond e Knox, MSSP 169, 2022, discutem esse vazamento no CWRU).

O autoencoder LSTM da versão anterior continua no código, com séries sintéticas, e não foi aplicado aqui: com uma única peça saudável, mais capacidade tende a memorizar melhor. O protocolo por tamanho é o teste que ele precisaria passar.

## 4. #052 — assinaturas no domínio da ordem

Assinatura: SES após pré-branqueamento, em dB acima da mediana móvel (41 bins), cortado em 0, reamostrado em ordens (0,5 a 16, passo 0,02) e normalizado. Base de comparação: eixo em Hz (15 a 480 Hz, passo 0,6). Correspondência pela média de classe mais próxima (cosseno).

| Biblioteca → consulta | Eixo | Normal | P. interna | Esfera | P. externa | Balanceada |
|---|---|---|---|---|---|---|
| 0 hp → 1–3 hp | ordens | 65 % | 100 % | 69 % | 67 % | 75,1 % |
| 0 hp → 1–3 hp | Hz | 65 % | 0 % | 46 % | 0 % | 27,6 % |
| outros tamanhos → tamanho novo | ordens | 84 % | 100 % | 44 % | 67 % | 73,7 % |
| outros tamanhos → tamanho novo | Hz | 78 % | 76 % | 44 % | 58 % | 64,1 % |

Uma mudança de 4 % na rotação desloca o terceiro harmônico de BPFI em quase 20 Hz; em hertz, a biblioteca deixa de reconhecer os defeitos de pista. Em ordens, a pista interna é reconhecida em todas as janelas, inclusive em peça nunca vista.

## 5. Testes (`tests/test_bearings.py`)

Ordens contra os valores do CWRU e identidades cinemáticas; pré-branqueamento com magnitude plana e fase preservada; envelope encontra o defeito simulado e não acusa ruído; curtose espectral aponta a ressonância e é ≈ 0 em ruído gaussiano; diagnóstico correto nos trechos reais de pista interna e externa; assinatura em ordens invariante à velocidade; AUC, Ledoit–Wolf e softmax.

## 6. Limites

Um rolamento por classe e tamanho, defeitos por eletroerosão (não desgaste natural), um único rolamento saudável, sensor do lado do acionamento a 12 kHz, rotação constante em cada registro.

## Referências

- Smith, W. A. e Randall, R. B. Rolling element bearing diagnostics using the Case Western Reserve University data: a benchmark study. *MSSP* 64–65, 2015.
- Randall, R. B. e Antoni, J. Rolling element bearing diagnostics — a tutorial. *MSSP* 25(2), 2011.
- Antoni, J. The spectral kurtosis: a useful tool for characterising non-stationary signals. *MSSP* 20(2), 2006.
- Randall, R. B. e Sawalhi, N. A new method for separating discrete components from a signal. *Sound and Vibration* 45(5), 2011.
- Ledoit, O. e Wolf, M. A well-conditioned estimator for large-dimensional covariance matrices. *J. Multivariate Analysis* 88(2), 2004.
- Hendriks, J., Dumond, P. e Knox, D. A. Towards better benchmarking using the CWRU bearing fault dataset. *MSSP* 169, 2022.
- Harris, T. A. e Kotzalas, M. N. *Rolling Bearing Analysis*, 5ª ed. CRC, 2006.
