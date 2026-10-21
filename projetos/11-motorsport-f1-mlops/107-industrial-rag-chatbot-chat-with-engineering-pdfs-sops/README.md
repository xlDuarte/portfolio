> **Estado auditado #107: protótipo matemático/numérico com entradas sintéticas, não um produto homologado.** Nomes de modelos, ferramentas, APIs, CV/RAG ou métricas no benchmark só indicam inspiração; **não demonstram** execução de terceiros (MLflow, TensorFlow, SHAP, CNN, serviços REST ou treino LSTM) sem código/imports, datasets e testes correspondentes. Não atribuir dados ou indicadores à F1 real.

# Project #107 — Assistente RAG Industrial — Chat com Manuais, SOPs e PDFs Técnicos
## Industrial RAG Chatbot — Chat with Engineering PDFs & SOPs

- **Categoria / Route:** `/projetos/motorsport-f1/107` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/107-industrial-rag-chatbot-chat-with-engineering-pdfs-sops`
- **Benchmark de Referência:** `Data Mavericks Adv 05 — Chat with Your Documents (LangChain, Vector DB)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Stack & Ferramentas:** `Python, FastF1/Telemetry, ChassisSim/QSS, FLIR Thermal, XGBoost, OpenCV, LangChain`
- **Fluxo de Engenharia (How It Flows):** `Telemetria GPS / Pneus -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Estratégia & Pista` (`GPS Telemetry / Tires -> Replay / EKF / FLIR -> ChassisSim / RAG / CNN -> Strategy & Track`)

---

## 1. Contexto Industrial & Automotivo (PT-BR)
Construção de chatbot Retrieval-Augmented Generation (RAG) com Python, LangChain e banco de dados vetorial para responder perguntas técnicas com citação direta de PDFs e manuais.

## 2. Industrial & Motorsport Context (EN-US)
Building a Retrieval-Augmented Generation (RAG) chatbot using Python, LangChain, and a Vector DB to answer engineering questions grounded directly in technical PDFs.

---

## 3. Como Executar / How to Run

```bash
python3 main.py
```
