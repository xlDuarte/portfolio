> **Auditoria técnica #107:** Gerador de PDF fictício, pypdf, LangChain split de documentos e retrieval TF-IDF com página e nome de arquivo. Não realiza chat gerado por LLM. **Stack efetiva:** LangChain, pypdf, ReportLab, Scikit-learn; respostas extrativas. Dados fictícios, nenhuma telemetria de F1 ou inspeção industrial autêntica, nenhuma homologação externa.

## Execução comprovável

```bash
python -m pip install -r requirements-motorsport-core.txt
python -m pip install -r requirements-motorsport-advanced.txt
python projetos/11-motorsport-f1-mlops/107-industrial-rag-chatbot-chat-with-engineering-pdfs-sops/main.py --run
```

**Código e testes:** [módulos executáveis](../../../motorsport_batch/README.md) e [suíte CI](../../../tests/test_motorsport_advanced.py). O modo padrão de inspeção de dados não treina os frameworks pesados; use `--run` para execução integral.

# Project #107 — Assistente RAG Industrial — Chat com Manuais, SOPs e PDFs Técnicos
## Industrial RAG Chatbot — Chat with Engineering PDFs & SOPs

- **Categoria / Route:** `/projetos/motorsport-f1/107` (`11 / 11`)
- **Diretório GitHub:** `projetos/11-motorsport-f1-mlops/107-industrial-rag-chatbot-chat-with-engineering-pdfs-sops`
- **Benchmark de Referência:** `Data Mavericks Adv 05 — Chat with Your Documents (LangChain, Vector DB)`
- **Autor:** Gabriel Reis Duarte (`@gabrielrduarte`)
- **Tecnologias de benchmark:** referências aspiracionais, não necessariamente implementadas neste caso.
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
