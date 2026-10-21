> **Estado auditado:** 111 entradas numeradas, das quais 5 agora executam estudos de caso com datasets sintéticos versionados, SQL/BI e/ou modelos treinados/avaliados; 95 permanecem demonstrações genéricas, além de 11 protótipos especializados Motorsport. Resultados dos 5 casos são exclusivamente sintéticos, nunca impacto corporativo observado. A meta 100/100 não é homologada; ver [QUALITY_ROADMAP.md](QUALITY_ROADMAP.md) e [case_studies](case_studies/README.md).

> **Aviso técnico:** este repositório contém protótipos demonstrativos e dados sintéticos. Resultados simulados não são resultados reais de treinamento, benchmarks ou integração com ferramentas externas. O módulo F1-PIP incluído é parcial e deve ser validado antes de ser anunciado como plataforma completa.

# Automotive & Industrial Engineering Lab — 110 Data, AI, F1, Porsche Cup & BI Projects
**Author:** Gabriel Reis Duarte (`@gabrielrduarte`)  
**Role:** Industrial Data Analyst | BI | Systems Integration (SAP/ARIBA/MES) & Motorsport Performance Engineering  
**Contact:** gabrielduartejardim@gmail.com | [LinkedIn](https://www.linkedin.com/in/gabrielrduarte)

---

## Destaques Principais (Flagship Motorsport Projects)
- **[#109 — Motor de Replay de Corrida F1 & Telemetria GPS em Tempo Real (Construído do Zero)](./projetos/11-motorsport-f1-mlops/109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch/)**
- **[#110 — Suíte Completa de Engenharia de Performance em Motorsport (Seminário Porsche Cup / Jorge Segers — 5 Dias Completos)](./projetos/11-motorsport-f1-mlops/110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim/)**

## Estrutura de Pastas do Repositório (`/projetos` — 11 Categorias / 110 Projetos)

### 01 / 10 — `01-dados` (Análise de Dados Industrial / Industrial Data Analysis)
- **Stack:** `Pandas, NumPy, Matplotlib, Jupyter, Power BI`
- **Pipeline:** `Ingestão SAP/CSV -> Limpeza ETL -> Exploração -> Insights KPI`

  - **[#001 — Desempenho de Treinamento e Operadores](./projetos/01-dados/001-operator-training-performance-analysis/)** (*Operator & Training Performance Analysis* | Ref: `01 Student Performance Analysis`)
  - **[#002 — Análise de Giro e Vendas de Reposição (Aftermarket)](./projetos/01-dados/002-aftermarket-auto-parts-sales-analysis/)** (*Aftermarket Auto Parts Sales Analysis* | Ref: `02 Supermarket Sales Analysis`)
  - **[#003 — Catálogo de Documentação Técnica e Telemetria](./projetos/01-dados/003-technical-documentation-telemetry-catalog/)** (*Technical Documentation & Telemetry Catalog* | Ref: `03 Netflix Content Analysis`)
  - **[#004 — Espectro Acústico e Vibração Veicular (NVH)](./projetos/01-dados/004-acoustic-nvh-vibration-spectrum-analysis/)** (*Acoustic NVH & Vibration Spectrum Analysis* | Ref: `04 Spotify Music Analysis`)
  - **[#005 — Engajamento em Trilhas de Capacitação Industrial](./projetos/01-dados/005-engineering-knowledge-base-analytics/)** (*Engineering Knowledge Base Analytics* | Ref: `05 YouTube Channel Analysis`)
  - **[#006 — Performance de Portal B2B e E-Procurement](./projetos/01-dados/006-b2b-industrial-e-procurement-analysis/)** (*B2B Industrial E-Procurement Analysis* | Ref: `06 E-commerce Sales Analysis`)
  - **[#007 — Comportamento de Requisições e Compras (OEM/Tier-1)](./projetos/01-dados/007-oem-tier-1-purchasing-behavior/)** (*OEM & Tier-1 Purchasing Behavior* | Ref: `07 Customer Purchase Analysis`)
  - **[#008 — Consumo de Utilidades e Operações de Turno](./projetos/01-dados/008-plant-shift-utilities-facility-analysis/)** (*Plant Shift Utilities & Facility Analysis* | Ref: `08 Restaurant Sales Analysis`)
  - **[#009 — Avaliação de Ativos Industriais e Imobilizado (CAPEX)](./projetos/01-dados/009-industrial-asset-facility-valuation/)** (*Industrial Asset & Facility Valuation* | Ref: `09 House Price Analysis`)
  - **[#010 — Impacto de Disrupções Globais na Cadeia Produtiva](./projetos/01-dados/010-supply-chain-disruption-impact-analysis/)** (*Supply Chain Disruption Impact Analysis* | Ref: `10 COVID-19 Data Analysis`)

### 02 / 10 — `02-eda` (Análise Exploratória (EDA) / Exploratory Data Analysis (EDA))
- **Stack:** `Pandas, Seaborn, Matplotlib, Plotly, SQL`
- **Pipeline:** `Dataset Bruto -> Distribuições -> Correlações -> Diagnóstico`

  - **[#011 — Demografia de Frota Global e Eletrificação](./projetos/02-eda/011-global-fleet-mobility-demographics-eda/)** (*Global Fleet & Mobility Demographics EDA* | Ref: `11 Global Population Analysis`)
  - **[#012 — Clima Organizacional, Segurança e Ergonomia Fabril](./projetos/02-eda/012-workplace-safety-ergonomics-index-eda/)** (*Workplace Safety & Ergonomics Index EDA* | Ref: `12 World Happiness Analysis`)
  - **[#013 — Capacidade de Armazéns e Centros de Distribuição](./projetos/02-eda/013-logistics-hub-warehouse-capacity-eda/)** (*Logistics Hub & Warehouse Capacity EDA* | Ref: `13 Airbnb Listings Analysis`)
  - **[#014 — Benchmarks de Telemetria e Tempos de Volta (Motorsport)](./projetos/02-eda/014-motorsport-telemetry-lap-benchmarks/)** (*Motorsport Telemetry & Lap Benchmarks* | Ref: `14 Olympic Games Analysis`)
  - **[#015 — Auditorias de Qualidade de Lotes e Fornecedores](./projetos/02-eda/015-component-quality-audit-ratings-eda/)** (*Component Quality Audit Ratings EDA* | Ref: `15 Movie Ratings Analysis`)
  - **[#016 — Telemetria de Pit-Stop e Troca Rápida de Ferramenta (SMED)](./projetos/02-eda/016-smed-high-speed-setup-telemetry-eda/)** (*SMED & High-Speed Setup Telemetry EDA* | Ref: `16 IPL Match Analysis`)
  - **[#017 — Mapeamento de Competências em Engenharia e Indústria 4.0](./projetos/02-eda/017-industrial-tech-talent-market-eda/)** (*Industrial & Tech Talent Market EDA* | Ref: `17 Job Market Analysis`)
  - **[#018 — Volatilidade de Ações Siderúrgicas e Automotivas](./projetos/02-eda/018-automotive-steel-equity-market-eda/)** (*Automotive & Steel Equity Market EDA* | Ref: `18 Stock Market EDA`)
  - **[#019 — Tempos de Despacho e Logística Inbound/Outbound](./projetos/02-eda/019-parts-dispatch-lead-time-eda/)** (*Parts Dispatch & Lead-Time EDA* | Ref: `19 Food Delivery Analysis`)
  - **[#020 — Causas-Raiz de Atrasos em Fretes Críticos e Aéreos](./projetos/02-eda/020-critical-freight-delay-root-cause-eda/)** (*Critical Freight Delay Root-Cause EDA* | Ref: `20 Flight Delay Analysis`)

### 03 / 10 — `03-regression` (Machine Learning: Regressão / Machine Learning: Regression)
- **Stack:** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Pipeline:** `Eng. Atributos -> Treinamento -> Avaliação R²/MAE -> Predição`

  - **[#021 — Estimativa de CAPEX para Instalações Industriais](./projetos/03-regression/021-industrial-facility-capex-valuation/)** (*Industrial Facility CAPEX Valuation* | Ref: `21 House Price Prediction`)
  - **[#022 — Valor Residual e Depreciação de Frota Automotiva](./projetos/03-regression/022-fleet-vehicle-residual-value-model/)** (*Fleet & Vehicle Residual Value Model* | Ref: `22 Used Car Price Prediction`)
  - **[#023 — Modelagem de Custos de Mão de Obra e Especialidades](./projetos/03-regression/023-engineering-compensation-cost-model/)** (*Engineering Compensation & Cost Model* | Ref: `23 Salary Prediction`)
  - **[#024 — Predição de Proficiência Técnica em Certificações](./projetos/03-regression/024-technical-certification-score-prediction/)** (*Technical Certification Score Prediction* | Ref: `24 Student Score Prediction`)
  - **[#025 — Projeção de Custos de Saúde Ocupacional e Sinistralidade](./projetos/03-regression/025-occupational-safety-cost-prediction/)** (*Occupational Safety Cost Prediction* | Ref: `25 Medical Cost Prediction`)
  - **[#026 — Precificação de Prêmio de Seguro de Maquinário e Frota](./projetos/03-regression/026-industrial-equipment-insurance-pricing/)** (*Industrial Equipment Insurance Pricing* | Ref: `26 Insurance Premium Prediction`)
  - **[#027 — Previsão de Volume de Vendas de Forjados e Cilindros](./projetos/03-regression/027-industrial-forgings-sales-regression/)** (*Industrial Forgings Sales Regression* | Ref: `27 Sales Forecasting`)
  - **[#028 — Dimensionamento de Custo de Hardware Industrial / Edge](./projetos/03-regression/028-edge-workstation-hardware-cost-model/)** (*Edge & Workstation Hardware Cost Model* | Ref: `28 Laptop Price Prediction`)
  - **[#029 — Predição de Consumo Elétrico em Fornos e Usinagem](./projetos/03-regression/029-furnace-machining-power-consumption/)** (*Furnace & Machining Power Consumption* | Ref: `29 Electricity Consumption Prediction`)
  - **[#030 — Estimativa de Lead-Time de Entrega Logística (ETA)](./projetos/03-regression/030-logistics-delivery-time-eta-prediction/)** (*Logistics Delivery Time (ETA) Prediction* | Ref: `30 Delivery Time Prediction`)

### 04 / 10 — `04-classification` (Machine Learning: Classificação / Machine Learning: Classification)
- **Stack:** `Scikit-learn, Pandas, XGBoost, Matplotlib`
- **Pipeline:** `Atributos -> Treino Modelo -> Matriz Confusão -> Classe Alvo`

  - **[#031 — Predição de Churn em Contratos B2B Industriais](./projetos/04-classification/031-b2b-industrial-contract-churn-prediction/)** (*B2B Industrial Contract Churn Prediction* | Ref: `31 Customer Churn Prediction`)
  - **[#032 — Aprovação Automatizada de Crédito para Fornecedores](./projetos/04-classification/032-vendor-b2b-credit-approval-classifier/)** (*Vendor & B2B Credit Approval Classifier* | Ref: `32 Loan Approval Prediction`)
  - **[#033 — Classificação de Risco de Contraparte e Compliance](./projetos/04-classification/033-counterparty-credit-compliance-risk/)** (*Counterparty Credit & Compliance Risk* | Ref: `33 Credit Risk Prediction`)
  - **[#034 — Predição de Rotatividade (Turnover) em Operações](./projetos/04-classification/034-shop-floor-tech-attrition-prediction/)** (*Shop-Floor & Tech Attrition Prediction* | Ref: `34 Employee Attrition Prediction`)
  - **[#035 — Triagem de Alertas de Cibersegurança e Phishing IT/OT](./projetos/04-classification/035-it-ot-cybersecurity-alert-classifier/)** (*IT/OT Cybersecurity Alert Classifier* | Ref: `35 Spam Email Detection`)
  - **[#036 — Diagnóstico de Falha Crítica em Bombas e Atuadores](./projetos/04-classification/036-hydraulic-pump-failure-classification/)** (*Hydraulic Pump Failure Classification* | Ref: `36 Heart Disease Prediction`)
  - **[#037 — Classificação de Degradação Química de Lubrificantes](./projetos/04-classification/037-lubricant-degradation-classifier/)** (*Lubricant Degradation Classifier* | Ref: `37 Diabetes Prediction`)
  - **[#038 — Detecção de Anomalias e Fraudes em Compras (SAP/SOX)](./projetos/04-classification/038-sap-procurement-anomaly-detection/)** (*SAP Procurement Anomaly Detection* | Ref: `38 Fraud Transaction Detection`)
  - **[#039 — Propensão de Recompra de Peças de Reposição](./projetos/04-classification/039-spare-parts-reorder-propensity-model/)** (*Spare Parts Reorder Propensity Model* | Ref: `39 Customer Purchase Prediction`)
  - **[#040 — Predição de Inadimplência e Quebra de SLA Contratual](./projetos/04-classification/040-contract-default-sla-breach-classifier/)** (*Contract Default & SLA Breach Classifier* | Ref: `40 Loan Default Prediction`)

### 05 / 10 — `05-nlp` (Processamento de Linguagem Natural / Natural Language Processing (NLP))
- **Stack:** `NLTK, spaCy, Hugging Face, Scikit-learn`
- **Pipeline:** `Texto Técnico -> Tokenização -> Modelo NLP -> Classificação`

  - **[#041 — Análise de Sentimento em Garantias e Pós-Venda](./projetos/05-nlp/041-warranty-field-feedback-sentiment/)** (*Warranty & Field Feedback Sentiment* | Ref: `41 Sentiment Analysis`)
  - **[#042 — Filtro Inteligente de Chamados de Service Desk](./projetos/05-nlp/042-service-desk-noise-ticket-filter/)** (*Service Desk Noise & Ticket Filter* | Ref: `42 Spam Message Detection`)
  - **[#043 — Verificação de Alertas Regulatórios e Supply Chain](./projetos/05-nlp/043-regulatory-supply-chain-alert-verifier/)** (*Regulatory & Supply Chain Alert Verifier* | Ref: `43 Fake News Detection`)
  - **[#044 — Classificação Automática de Ordens de Manutenção (SAP PM)](./projetos/05-nlp/044-sap-pm-work-order-topic-classifier/)** (*SAP PM Work-Order Topic Classifier* | Ref: `44 News Topic Classification`)
  - **[#045 — Análise de Polaridade em Laudos de Inspeção Técnica](./projetos/05-nlp/045-technical-inspection-report-polarity/)** (*Technical Inspection Report Polarity* | Ref: `45 Movie Review Classification`)
  - **[#046 — Triagem Semântica de Currículos de Engenharia e TI](./projetos/05-nlp/046-engineering-tech-resume-classifier/)** (*Engineering & Tech Resume Classifier* | Ref: `46 Resume Classification`)
  - **[#047 — Detecção de Criticidade e Urgência em Diários de Bordo](./projetos/05-nlp/047-shift-log-criticality-urgency-nlp/)** (*Shift-Log Criticality & Urgency NLP* | Ref: `47 Text Emotion Detection`)
  - **[#048 — Scanner de Conformidade Ética e Governança Corporativa](./projetos/05-nlp/048-compliance-governance-text-scanner/)** (*Compliance & Governance Text Scanner* | Ref: `48 Toxic Comment Detection`)
  - **[#049 — Roteador Multilíngue de Documentação Global (PT/EN/ES)](./projetos/05-nlp/049-multi-plant-documentation-language-router/)** (*Multi-Plant Documentation Language Router* | Ref: `49 Language Detection`)
  - **[#050 — Sumarização Executiva de Normas ISO, SOPs e Contratos](./projetos/05-nlp/050-sop-iso-contract-summarizer/)** (*SOP, ISO & Contract Summarizer* | Ref: `50 News Article Summarization`)

### 06 / 10 — `06-recommendation` (Sistemas de Recomendação / Recommendation Systems)
- **Stack:** `Pandas, NumPy, Scikit-learn, Streamlit`
- **Pipeline:** `Perfil / Ativo -> Similaridade -> Ranking -> Top-N Ações`

  - **[#051 — Recomendador de Playbooks e Vídeos de Manutenção](./projetos/06-recommendation/051-maintenance-playbook-video-recommender/)** (*Maintenance Playbook Video Recommender* | Ref: `51 Movie Recommendation System`)
  - **[#052 — Matcher de Assinaturas Acústicas de Diagnóstico](./projetos/06-recommendation/052-acoustic-diagnostic-signature-matcher/)** (*Acoustic Diagnostic Signature Matcher* | Ref: `52 Music Recommendation System`)
  - **[#053 — Recomendador de Normas Técnicas e Manuais de Engenharia](./projetos/06-recommendation/053-engineering-standard-manual-finder/)** (*Engineering Standard & Manual Finder* | Ref: `53 Book Recommendation System`)
  - **[#054 — Recomendação Cruzada de Ferramentaria e Insumos (MRO)](./projetos/06-recommendation/054-tooling-spare-parts-recommender/)** (*Tooling & Spare Parts Recommender* | Ref: `54 Product Recommendation System`)
  - **[#055 — Trilha Recomendada de Capacitação (Six Sigma / Dados)](./projetos/06-recommendation/055-industrial-upskilling-path-recommender/)** (*Industrial Upskilling Path Recommender* | Ref: `55 Course Recommendation System`)
  - **[#056 — Alocação Inteligente de Engenheiros por Projeto](./projetos/06-recommendation/056-project-to-engineer-skill-matcher/)** (*Project-to-Engineer Skill Matcher* | Ref: `56 Job Recommendation System`)
  - **[#057 — Feed Personalizado de Inteligência de Commodities e Setor](./projetos/06-recommendation/057-industrial-market-intelligence-feed/)** (*Industrial Market Intelligence Feed* | Ref: `57 News Recommendation System`)
  - **[#058 — Recomendador de Fornecedores Homologados (ARIBA)](./projetos/06-recommendation/058-approved-supplier-recommender-ariba/)** (*Approved Supplier Recommender (Ariba)* | Ref: `58 Restaurant Recommendation System`)
  - **[#059 — Recomendador de Rotas e Modais Logísticos](./projetos/06-recommendation/059-optimal-logistics-route-carrier-engine/)** (*Optimal Logistics Route & Carrier Engine* | Ref: `59 Travel Destination Recommendation`)
  - **[#060 — Otimizador de Lotes de Compra e Kits de Manutenção](./projetos/06-recommendation/060-automated-bom-maintenance-kit-engine/)** (*Automated BOM & Maintenance Kit Engine* | Ref: `60 Personalized Shopping Recommendation`)

### 07 / 10 — `07-timeseries` (Séries Temporais & Forecasting / Time Series & Forecasting)
- **Stack:** `Pandas, Statsmodels, Prophet, Plotly`
- **Pipeline:** `Série Histórica -> Tendência + Sazonal -> Forecast -> Erro MAPE`

  - **[#061 — Forecasting de Preços de Aço, Ligas Metálicas e Insumos](./projetos/07-timeseries/061-steel-alloy-commodity-forecasting/)** (*Steel & Alloy Commodity Forecasting* | Ref: `61 Stock Price Analysis & Forecasting`)
  - **[#062 — Previsão S&OP de Faturamento e Demanda Industrial](./projetos/07-timeseries/062-s-op-industrial-sales-forecasting/)** (*S&OP Industrial Sales Forecasting* | Ref: `62 Sales Forecasting`)
  - **[#063 — Previsão Termodinâmica e Impacto Climático na Planta](./projetos/07-timeseries/063-plant-thermal-load-weather-forecast/)** (*Plant Thermal Load & Weather Forecast* | Ref: `63 Weather Forecasting`)
  - **[#064 — Forecasting de Demanda de Energia em Horário de Ponta](./projetos/07-timeseries/064-rolling-mill-electricity-demand-forecast/)** (*Rolling Mill Electricity Demand Forecast* | Ref: `64 Electricity Demand Forecasting`)
  - **[#065 — Previsão de Tráfego de Mensagens IIoT e APIs Corporativas](./projetos/07-timeseries/065-iiot-broker-api-traffic-forecasting/)** (*IIoT Broker & API Traffic Forecasting* | Ref: `65 Website Traffic Forecasting`)
  - **[#066 — Previsão de Consumo de Ferramentaria e ICS Críticos](./projetos/07-timeseries/066-critical-ics-tooling-demand-forecast/)** (*Critical ICS & Tooling Demand Forecast* | Ref: `66 Retail Demand Forecasting`)
  - **[#067 — Previsão de Ocupação de Centros de Usinagem e Docas](./projetos/07-timeseries/067-machining-center-dock-slot-forecast/)** (*Machining Center & Dock Slot Forecast* | Ref: `67 Hotel Booking Forecasting`)
  - **[#068 — Análise de Volatilidade Cambial em Importação de Insumos](./projetos/07-timeseries/068-fx-volatility-analysis-for-imports/)** (*FX Volatility Analysis for Imports* | Ref: `68 Cryptocurrency Price Analysis`)
  - **[#069 — Monitoramento e Previsão de Emissões Atmosféricas (ESG)](./projetos/07-timeseries/069-industrial-esg-emissions-forecasting/)** (*Industrial ESG Emissions Forecasting* | Ref: `69 Air Quality Forecasting`)
  - **[#070 — Previsão de Taxa de Consumo (Burn-Rate) de Insumos Químicos](./projetos/07-timeseries/070-consumables-burn-rate-forecasting/)** (*Consumables Burn-Rate Forecasting* | Ref: `70 Food Demand Forecasting`)

### 08 / 10 — `08-vision` (Visão Computacional Industrial / Industrial Computer Vision)
- **Stack:** `OpenCV, TensorFlow, PyTorch, NumPy`
- **Pipeline:** `Câmera Industrial -> Pré-processo -> Rede CNN -> Detecção`

  - **[#071 — Verificação Automática de EPIs no Chão de Fábrica](./projetos/08-vision/071-shop-floor-ppe-compliance-detection/)** (*Shop-Floor PPE Compliance Detection* | Ref: `71 Face Mask Detection`)
  - **[#072 — Interface HMI sem Toque por Gestos para Operadores](./projetos/08-vision/072-touchless-hmi-hand-gesture-control/)** (*Touchless HMI Hand Gesture Control* | Ref: `72 Hand Gesture Recognition`)
  - **[#073 — Detecção e Contagem de Peças Forjadas e Estampadas](./projetos/08-vision/073-forged-stamped-part-detection/)** (*Forged & Stamped Part Detection* | Ref: `73 Object Detection System`)
  - **[#074 — Monitoramento de Fadiga e Atenção em Operadores/Frota](./projetos/08-vision/074-operator-driver-fatigue-monitoring/)** (*Operator & Driver Fatigue Monitoring* | Ref: `74 Facial Emotion Recognition`)
  - **[#075 — Reconhecimento Óptico (OCR) de Gravações em Relevo/Punção](./projetos/08-vision/075-stamped-serial-die-cast-ocr/)** (*Stamped Serial & Die-Cast OCR* | Ref: `75 Handwritten Digit Recognition`)
  - **[#076 — Detecção de Trincas Superficiais, Porosidade e Oxidação](./projetos/08-vision/076-surface-crack-oxidation-detection/)** (*Surface Crack & Oxidation Detection* | Ref: `76 Plant Disease Detection`)
  - **[#077 — Reconhecimento de Sinalização para AGVs e Sistemas ADAS](./projetos/08-vision/077-agv-adas-traffic-sign-recognition/)** (*AGV & ADAS Traffic Sign Recognition* | Ref: `77 Traffic Sign Recognition`)
  - **[#078 — Classificação Automática de Sucata Metálica e Resíduos](./projetos/08-vision/078-scrap-metal-recycling-classifier/)** (*Scrap Metal & Recycling Classifier* | Ref: `78 Waste Classification`)
  - **[#079 — Rastreamento de Caminhões e Movimentação no Pátio](./projetos/08-vision/079-plant-yard-vehicle-fleet-tracking/)** (*Plant Yard Vehicle & Fleet Tracking* | Ref: `79 Vehicle Detection`)
  - **[#080 — Classificação de Microestrutura Metalográfica por Imagem](./projetos/08-vision/080-metallurgical-microstructure-classifier/)** (*Metallurgical Microstructure Classifier* | Ref: `80 Food Image Classification`)

### 09 / 10 — `09-business` (Business Intelligence & Finanças / Business & Finance Analytics)
- **Stack:** `SQL, Power BI, DAX, Scikit-learn, SAP`
- **Pipeline:** `Dados SAP/ERP -> Modelagem DAX -> Dashboard BI -> Decisão ROI`

  - **[#081 — Predição de Lifetime Value (LTV) de Contas Industriais](./projetos/09-business/081-b2b-account-lifetime-value-ltv/)** (*B2B Account Lifetime Value (LTV)* | Ref: `81 Customer Lifetime Value Prediction`)
  - **[#082 — Dashboard Executivo de OEE, Cotas e Performance (Gerdau)](./projetos/09-business/082-executive-oee-commercial-bi-dashboard/)** (*Executive OEE & Commercial BI Dashboard* | Ref: `82 Sales Dashboard & Insights`)
  - **[#083 — Análise de Retorno de Iniciativas Comerciais e Feiras B2B](./projetos/09-business/083-b2b-commercial-campaign-roi-analysis/)** (*B2B Commercial Campaign ROI Analysis* | Ref: `83 Marketing Campaign Analysis`)
  - **[#084 — Segmentação ABC/RFM de Fornecedores e Clientes](./projetos/09-business/084-supplier-client-abc-rfm-segmentation/)** (*Supplier & Client ABC/RFM Segmentation* | Ref: `84 Customer Segmentation`)
  - **[#085 — Auditoria Contínua de Pagamentos e Conformidade SOX](./projetos/09-business/085-sox-payment-audit-anomaly-detection/)** (*SOX Payment Audit & Anomaly Detection* | Ref: `85 Credit Card Fraud Detection`)
  - **[#086 — Matriz de Risco e Heatmap Operacional (Sistema Prontos)](./projetos/09-business/086-operational-risk-matrix-heatmap/)** (*Operational Risk Matrix & Heatmap* | Ref: `86 Financial Risk Analysis`)
  - **[#087 — Otimização de Portfólio de Projetos de Inovação (CAPEX)](./projetos/09-business/087-capex-innovation-portfolio-analysis/)** (*CAPEX Innovation Portfolio Analysis* | Ref: `87 Portfolio Analysis`)
  - **[#088 — Projeção de Faturamento e Conciliação Contábil-Fiscal](./projetos/09-business/088-industrial-billing-revenue-projection/)** (*Industrial Billing & Revenue Projection* | Ref: `88 Revenue Prediction`)
  - **[#089 — Spend Analytics e Eficiência de Compras no SAP Ariba](./projetos/09-business/089-sap-ariba-procurement-spend-analytics/)** (*SAP Ariba Procurement Spend Analytics* | Ref: `89 E-commerce Customer Analytics`)
  - **[#090 — Análise de Custos de Transformação, Tarifas e Horas Extras](./projetos/09-business/090-manufacturing-cost-tariff-analytics/)** (*Manufacturing Cost & Tariff Analytics* | Ref: `90 Employee Salary Analysis`)

### 10 / 10 — `10-advanced` (Sistemas Avançados Ponta a Ponta / Advanced End-to-End Systems)
- **Stack:** `Docker, FastAPI, Kafka, Streamlit, Power BI`
- **Pipeline:** `Stream IIoT/SAP -> Pipeline ETL -> Modelo IA/BI -> Deploy Prod`

  - **[#091 — Motor End-to-End de Governança e Risco de Fornecedores](./projetos/10-advanced/091-end-to-end-vendor-governance-risk-engine/)** (*End-to-End Vendor Governance & Risk Engine* | Ref: `91 End-to-End Credit Risk System`)
  - **[#092 — Monitoramento em Tempo Real de Anomalias Transacionais ERP](./projetos/10-advanced/092-real-time-erp-ot-anomaly-detection/)** (*Real-Time ERP/OT Anomaly Detection* | Ref: `92 Real-Time Fraud Detection`)
  - **[#093 — Plataforma IA de Mapeamento de Competências Técnicas](./projetos/10-advanced/093-ai-technical-competency-screening-platform/)** (*AI Technical Competency Screening Platform* | Ref: `93 AI-Powered Resume Screening`)
  - **[#094 — Sistema Integrado de Previsão de Demanda e Estoque Crítico](./projetos/10-advanced/094-integrated-s-op-ics-demand-system/)** (*Integrated S&OP & ICS Demand System* | Ref: `94 Demand Prediction System`)
  - **[#095 — Plataforma de Retenção e Saúde de Contratos B2B](./projetos/10-advanced/095-enterprise-b2b-contract-retention-platform/)** (*Enterprise B2B Contract Retention Platform* | Ref: `95 Customer Churn Prediction Platform`)
  - **[#096 — Motor de Recomendação de Parâmetros de Setup (MES)](./projetos/10-advanced/096-real-time-mes-setup-recommendation-engine/)** (*Real-Time MES Setup Recommendation Engine* | Ref: `96 Real-Time Recommendation Engine`)
  - **[#097 — Plataforma Ciberfísica de Manutenção Preditiva (RUL)](./projetos/10-advanced/097-cyber-physical-predictive-maintenance-system/)** (*Cyber-Physical Predictive Maintenance System* | Ref: `97 Predictive Maintenance System`)
  - **[#098 — Classificador Inteligente de Desenhos Técnicos, NFs e Contratos](./projetos/10-advanced/098-ai-engineering-document-invoice-classifier/)** (*AI Engineering Document & Invoice Classifier* | Ref: `98 AI-Based Document Classification`)
  - **[#099 — Centro de Comando em Tempo Real de Qualidade e Segurança](./projetos/10-advanced/099-real-time-quality-safety-command-center/)** (*Real-Time Quality & Safety Command Center* | Ref: `99 Real-Time Sentiment Analysis Dashboard`)
  - **[#100 — Plataforma Corporativa End-to-End de Business Intelligence](./projetos/10-advanced/100-end-to-end-industrial-bi-data-platform/)** (*End-to-End Industrial BI & Data Platform* | Ref: `100 End-to-End Business Intelligence Platform`)

### 11 / 11 — `11-motorsport-f1-mlops` (Motorsport F1, Porsche Cup & MLOps Avançado / Motorsport F1, Porsche Cup & Advanced MLOps)
- **Stack:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Pipeline:** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista`

  - **[#101 — Estratégia Preditiva de Corrida (F1) & Simulador de Janela de Pit-Stop](./projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator/)** (*F1 Predictive Race Strategy & Pit-Stop Window Simulator* | Ref: `F1 Skill 01 — Predictive Race Strategy (XGBoost / Random Forest)`)
  - **[#102 — Estimação de Estado em Dinâmica Veicular com Filtro de Kalman Estendido (EKF)](./projetos/11-motorsport-f1-mlops/102-vehicle-dynamics-state-estimation-via-extended-kalman-filter-ekf/)** (*Vehicle Dynamics State Estimation via Extended Kalman Filter (EKF)* | Ref: `F1 Skill 02 — State Estimation (Vehicle Dynamics EKF)`)
  - **[#103 — Visão Computacional Onboard (F1) — Rastreamento em Frenagem e Curvas](./projetos/11-motorsport-f1-mlops/103-motorsport-onboard-video-feature-tracking-motion-calibration/)** (*Motorsport Onboard Video Feature Tracking & Motion Calibration* | Ref: `F1 Skill 03 — Computer Vision (Motorsport Video Analysis)`)
  - **[#104 — Detecção de Anomalias em Vibração Mecânica com Rede LSTM vs. Baseline](./projetos/11-motorsport-f1-mlops/104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline/)** (*Mechanical Vibration Time-Series Anomaly Detection (LSTM vs. Baseline)* | Ref: `F1 Skill 04 & Data Mavericks Adv 06 — LSTM Time-Series Anomaly Detection`)
  - **[#105 — Inspeção Radiográfica Industrial (Raio-X NDT) com CNN & Grad-CAM](./projetos/11-motorsport-f1-mlops/105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam/)** (*Industrial X-Ray NDT Defect Detection with CNN & Grad-CAM* | Ref: `Data Mavericks Adv 01 — X-Ray CNN with Grad-CAM & Transfer Learning`)
  - **[#106 — Pipeline MLOps End-to-End com MLflow, Docker & Deploy FastAPI](./projetos/11-motorsport-f1-mlops/106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi/)** (*End-to-End MLOps Pipeline with MLflow, Docker & FastAPI* | Ref: `Data Mavericks Adv 04 — End to End ML Pipeline (FastAPI, Docker, MLflow)`)
  - **[#107 — Assistente RAG Industrial — Chat com Manuais, SOPs e PDFs Técnicos](./projetos/11-motorsport-f1-mlops/107-industrial-rag-chatbot-chat-with-engineering-pdfs-sops/)** (*Industrial RAG Chatbot — Chat with Engineering PDFs & SOPs* | Ref: `Data Mavericks Adv 05 — Chat with Your Documents (LangChain, Vector DB)`)
  - **[#108 — Explicabilidade de Modelos (SHAP) & Eventos Raros com SMOTE](./projetos/11-motorsport-f1-mlops/108-explainable-ai-shap-imbalanced-fault-risk-modeling-with-smote/)** (*Explainable AI (SHAP) & Imbalanced Fault/Risk Modeling with SMOTE* | Ref: `Data Mavericks Int 01/02/05 — Explainable AI (SHAP) & Imbalanced SMOTE`)
  - **[#109 — Motor de Replay de Corrida F1 & Telemetria GPS em Tempo Real (Construído do Zero)](./projetos/11-motorsport-f1-mlops/109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch/)** (*F1 Telemetry Race Replay & Live GPS Track Position Engine (Built from Scratch)* | Ref: `Flagship #109 — Ground-Up 2D/3D Race Replay, Live Timing Tower & Delta Engine`)
  - **[#110 — Suíte Completa de Engenharia de Performance em Motorsport (Pneus, FLIR, Setup, HH Timing & Laptime Sim)](./projetos/11-motorsport-f1-mlops/110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim/)** (*Complete Motorsport Performance Engineering Suite (Tire Physics, FLIR, Setup, HH Timing & Laptime Sim)* | Ref: `Flagship #110 — Full 5-Day Motorsport Performance Engineering Seminar Suite (Porsche Cup / WEC)`)


## Auditoria incremental — lote Data Analysis #001–#009

**9 projetos específicos implementados e testados** com Pandas, NumPy, Matplotlib e notebooks Jupyter, além de 9 CSVs artificiais versionados, testes de esquema e relatórios SVG. Veja [`analytics_batch1/README.md`](analytics_batch1/README.md), [`tests/test_analytics_batch1.py`](tests/test_analytics_batch1.py) e as páginas `site/cases/001/` a `site/cases/009/`.

Os resultados são **inteiramente sintéticos** e Power BI continua **pendente de PBIX/PBIP testado**. **Os projetos #011–#100 ainda não estão todos completos**. O objetivo de 100/100 permanece aberto.


## Lote EDA #011–#020 (outubro de 2026)

Dez projetos independentes com métricas específicas, CSVs sintéticos versionados, Pandas/NumPy, consultas SQL SQLite, Seaborn/Matplotlib (SVG), Plotly (HTML), notebooks Jupyter e testes negativos. Catálogo online: `/cases/eda/`.

```bash
pip install -r requirements-case-studies.txt -r requirements-eda.txt
python -m analytics_eda.generate
python -m analytics_eda.engine 11 --report-dir /tmp/fleet-eda
python -m unittest discover -s tests -v
```

**Limites:** dados sintéticos, sem inferência causal/observação empresarial real. Plotly HTML usa CDN para interatividade.


## Regressão #021–#030 — lote reproduzível

Nove estudos #022–#030 receberam implementações próprias de regressão treinada com Pandas, Scikit-learn, XGBoost e Matplotlib, bases sintéticas distintas, separações explícitas e métricas em holdout. O modelo #021 foi preservado e passou a ter página. Veja [catálogo de regressão](site/cases/regression/index.html), [relatório técnico](BATCH_021_030_REPORT.md) e [código](regression_batch/engine.py).

```bash
python -m pip install -r requirements-regression.txt
python -m unittest discover -s tests -v
python -m regression_batch.engine 22 --save
```

Resultados sintéticos não equivalem a validação em dados do mundo real ou benefícios empresariais observados.
