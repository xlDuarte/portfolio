"""Content model for the static portfolio site.

Single source of truth for navigation, niches, categories and the projects that
are not part of the generated industrial catalogue (``site/industry/catalog``
data covers #001–#100). ``build_site.py`` renders every hub page from here.
"""
from __future__ import annotations

SITE_URL = "https://gabriel-automotive-industrial-lab.vercel.app"
REPO_URL = "https://github.com/xlDuarte/portfolio"
LINKEDIN_URL = "https://www.linkedin.com/in/gabrielrduarte"
AUTHOR = "Gabriel Reis Duarte"

NAV = [
    ("industrial", "Industrial", "/industrial/"),
    ("automotivo", "Automotivo", "/automotivo/"),
    ("laboratorio", "Laboratório", "/laboratorio/"),
    ("sobre", "Sobre", "/sobre/"),
]

# Industrial catalogue: plain-language names for the ten domains.
DOMAINS = {
    "dados": ("Análise de dados", "Pandas, NumPy e Matplotlib sobre operações, compras e utilidades."),
    "eda": ("Análise exploratória", "Distribuições, correlações e SQL com gráficos interativos."),
    "regression": ("Regressão", "Scikit-learn e XGBoost contra baseline, com MAE e R² em holdout."),
    "classification": ("Classificação", "Treino, calibração e teste separados; limiar escolhido fora do teste."),
    "nlp": ("Texto e documentos", "Classificadores de texto com baseline e teste em modelos não vistos."),
    "recommendation": ("Recomendação", "TF-IDF, similaridade e regras de negócio para ranking."),
    "timeseries": ("Séries temporais", "Backtesting walk-forward, ETS e Prophet contra baseline sazonal."),
    "vision": ("Visão computacional", "OpenCV e CNNs treinadas em imagens geradas."),
    "business": ("BI e finanças", "SQL em SQLite, indicadores, Power Query e DAX."),
    "advanced": ("Sistemas ponta a ponta", "FastAPI, SQLite e Kafka/Redpanda de teste."),
}

# Fully written industrial case studies (own write-up, dataset, chart, code).
INDUSTRIAL_FEATURED = [
    {"slug": "oee", "title": "Eficiência fabril com OEE ponderado",
     "desc": "OEE agregado pelo tempo programado, não pela média simples entre linhas. Mostra onde estão as perdas de disponibilidade e refugo.",
     "tags": ["Python", "SQL", "Pandas"]},
    {"slug": "supply", "title": "Supply chain: OTIF e ruptura",
     "desc": "Pedido entregue completo e no prazo, com exposição financeira das faltas por fornecedor.",
     "tags": ["Python", "SQL"]},
    {"slug": "capex", "title": "CAPEX com regressão Ridge",
     "desc": "Pipeline scikit-learn ajustado só no treino, comparado a baseline com MAE e RMSE em holdout.",
     "tags": ["scikit-learn", "Ridge"]},
    {"slug": "forecast", "title": "Previsão de demanda",
     "desc": "Backtesting em janelas móveis e erro por horizonte, contra um baseline ingênuo.",
     "tags": ["Séries temporais"]},
    {"slug": "churn", "title": "Risco de churn B2B",
     "desc": "Classificador com limiar definido na calibração e métricas reportadas no teste intocado.",
     "tags": ["Classificação"]},
]

# Projects from the numbered catalogue that are the most complete implementations.
INDUSTRIAL_STRONG = {22, 31, 61, 81, 91}

# Automotive and shared projects (#101–#111) plus the interactive F1 labs.
F1_TOOLS = [
    {"title": "Modelos e probabilidades de corrida", "path": "/motorsport/f1-pip/", "id": 111,
     "desc": "Oito modelos ajustados em resultados reais de 2022 a 2024, validação temporal e simulação Monte Carlo de cenários.",
     "tags": ["Dados reais", "Monte Carlo", "scikit-learn"]},
    {"title": "Análise de corrida em cinco ferramentas", "path": "/motorsport/insights/",
     "desc": "Comparação de curvas, probabilidade de pódio, cenários de campeonato, ritmo de corrida e trajetória.",
     "tags": ["OpenF1", "FastF1"]},
    {"title": "Aerodinâmica ativa", "path": "/motorsport/active-aero/",
     "desc": "Compromisso entre carga e arrasto sobre velocidade medida; importa coeficientes de CFD ou ensaio.",
     "tags": ["Física", "Telemetria real"]},
    {"title": "Recuperação de energia", "path": "/motorsport/energy-recovery/",
     "desc": "Energia recuperável na frenagem, perdas de conversão e estado de carga estimado ao longo da volta.",
     "tags": ["Física", "Telemetria real"]},
    {"title": "Simulador de tempo de volta", "path": "/motorsport/lap-simulator/",
     "desc": "Pneu Pacejka, transferência de carga e envelope g-g-V em 3D, calibrados na telemetria de Verstappen: volta simulada em 96,79 s contra 96,75 s reais.",
     "tags": ["Física", "Telemetria real", "Calibração bayesiana"]},
]

F1_PROJECTS = [
    {"id": 101, "title": "Estratégia de pneus e janela de pit-stop", "path": "/cases/motorsport/101/",
     "code": "projetos/11-motorsport-f1-mlops/101-f1-predictive-race-strategy-pit-stop-window-simulator",
     "desc": "Ritmo estimado a partir de 1.004 voltas observadas no Bahrein 2024; compara planos de parada.",
     "tags": ["Dados reais", "XGBoost"]},
    {"id": 102, "title": "Telemetria e filtro de Kalman", "path": "/cases/motorsport/102/",
     "code": "projetos/11-motorsport-f1-mlops/102-vehicle-dynamics-state-estimation-via-extended-kalman-filter-ekf",
     "desc": "Velocidade, RPM, acelerador e freio medidos via OpenF1; compara sensor, referência e filtro.",
     "tags": ["Dados reais", "EKF"]},
    {"id": 107, "title": "Arquivo da direção de prova", "path": "/cases/motorsport/107/",
     "code": "projetos/11-motorsport-f1-mlops/107-industrial-rag-chatbot-chat-with-engineering-pdfs-sops",
     "desc": "Busca nas mensagens oficiais da direção de prova registradas no GP do Bahrein 2024.",
     "tags": ["Dados reais", "Busca"]},
    {"id": 109, "title": "Replay de corrida", "path": "/cases/motorsport/109/",
     "code": "projetos/11-motorsport-f1-mlops/109-f1-telemetry-race-replay-live-gps-track-position-engine-built-from-scratch",
     "desc": "Pista navegável, classificação e telemetria sincronizadas em quatro minutos da corrida do Bahrein 2024.",
     "tags": ["Dados reais", "Visualização"]},
]

PORSCHE_PROJECT = {
    "id": 110, "title": "Laboratório de engenharia Porsche Cup", "path": "/cases/motorsport/110/",
    "code": "projetos/11-motorsport-f1-mlops/110-complete-motorsport-performance-engineering-suite-tire-physics-flir-setup-hh-timing-laptime-sim",
    "desc": "Carga por roda, temperatura dos pneus e dinâmica veicular a partir de uma aquisição importada do carro.",
}
PORSCHE_MODULES = [
    {"title": "Aquisição e quatro rodas", "anchor": "#demo",
     "desc": "Importa a aquisição do carro e sincroniza cargas, temperaturas de pneu e acelerações no mesmo instante."},
    {"title": "Análises de engenharia", "anchor": "#seminar",
     "desc": "Transferência de carga, equilíbrio, frenagem e tração, mapeados ao conteúdo técnico de um seminário de engenharia de pista."},
    {"title": "Fluxo de evento", "anchor": "#seminar",
     "desc": "Da importação ao relatório: checagem de canais, comparação entre voltas e exportação dos resultados."},
]

SHARED_PROJECTS = [
    {"id": 103, "title": "Visão computacional em vídeo onboard", "path": "/cases/motorsport/103/",
     "code": "projetos/11-motorsport-f1-mlops/103-motorsport-onboard-video-feature-tracking-motion-calibration",
     "desc": "Rastreamento de pontos e fluxo óptico. Serve a câmeras de linha de produção e a vídeo onboard.",
     "both": "Inspeção de linha e vídeo de pista"},
    {"id": 104, "title": "Detecção de anomalias em vibração", "path": "/cases/motorsport/104/",
     "code": "projetos/11-motorsport-f1-mlops/104-mechanical-vibration-time-series-anomaly-detection-lstm-vs-baseline",
     "desc": "Autoencoder LSTM contra baseline RMS em sinais de acelerômetro.",
     "both": "Mancais e motores; suspensão e transmissão"},
    {"id": 105, "title": "Inspeção radiográfica com CNN e Grad-CAM", "path": "/cases/motorsport/105/",
     "code": "projetos/11-motorsport-f1-mlops/105-industrial-x-ray-ndt-defect-detection-with-cnn-grad-cam",
     "desc": "Classificação de defeitos em radiografias geradas, com mapas de explicação visual.",
     "both": "Peças fundidas e soldas; componentes de chassi"},
    {"id": 106, "title": "MLOps com MLflow e FastAPI", "path": "/cases/motorsport/106/",
     "code": "projetos/11-motorsport-f1-mlops/106-end-to-end-mlops-pipeline-with-mlflow-docker-fastapi",
     "desc": "Rastreamento de experimentos, artefatos recarregáveis e serviço de inferência em contêiner.",
     "both": "Qualquer modelo que vá para produção"},
    {"id": 108, "title": "Explicabilidade em risco de falha", "path": "/cases/motorsport/108/",
     "code": "projetos/11-motorsport-f1-mlops/108-explainable-ai-shap-imbalanced-fault-risk-modeling-with-smote",
     "desc": "SHAP sobre um modelo de falha com classes desbalanceadas e SMOTE apenas no treino.",
     "both": "Manutenção industrial e confiabilidade do carro"},
]

# Old URLs → new destinations. Used by vercel.json and by the GitHub Pages stubs.
REDIRECTS = {
    "/prototipos/heroi/": "/",
    "/industry/": "/industrial/",
    "/industry/arquivo": "/industrial/",
    "/industry/arquivo.html": "/industrial/",
    "/motorsport/": "/automotivo/",
    "/motorsport/racing/": "/automotivo/f1/",
    "/f1/": "/automotivo/f1/",
    "/f1-models/": "/motorsport/f1-pip/",
    "/about/": "/sobre/",
    "/docs/": "/industrial/#catalogo",
    "/releases/": "/sobre/#versoes",
    "/packages/": "/sobre/#versoes",
    "/cases/": "/industrial/",
    **{f"/cases/nlp/{n}/": f"/cases/nlp/{n:03d}/" for n in range(41, 51)},
}

EXPERIENCE = [
    ("2024 – 2026", "Gerdau Summit · Pindamonhangaba, SP",
     "Estágio em análise de dados, ambiente industrial",
     "Dashboards de OEE e logística em Power BI, ETL com Power Query, Python e SQL, automações com Power Automate e VBA, apoio à governança de dados ligada a SAP, Ariba e MES em Supply Chain, Logística e Controladoria."),
    ("2022 – 2025", "Revelo Brasil", "Redação técnica em tecnologia",
     "Documentação e guias sobre BI, ETL, DAX, Python, nuvem e governança de dados."),
    ("2022 – 2023", "Kroton Educacional", "Estágio em desenvolvimento backend",
     "Microsserviços em Java, integração com MongoDB, ETL e documentação de APIs."),
    ("2017 – 2022", "Advocacia empresarial", "Advogado · tributário, empresarial e compliance",
     "Riscos regulatórios, conformidade contratual e LGPD. OAB ativa."),
]

EDUCATION = [
    "Bacharelado em Ciência da Computação (conclusão em 2026)",
    "Tecnólogo em Análise e Desenvolvimento de Sistemas (2022)",
    "Pós-graduação em Gestão Financeira e Tributária (UNITAU, 2020)",
    "Bacharelado em Direito · OAB ativa",
    "Certificações: LGPD, Lean Six Sigma Yellow Belt (FM2S), inglês C2 (EF SET)",
]
