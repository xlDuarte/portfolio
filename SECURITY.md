# Política de segurança

Os sistemas deste portfólio são **demonstrativos** e não constituem plataforma de produção nem sistema industrial certificado.

Relate vulnerabilidades por **Private vulnerability reporting** do GitHub (se o recurso estiver disponível) ou por contato privado com o mantenedor. Não publique credenciais ou detalhes exploráveis em issues abertas.

## Regras

- Jamais versionar `.env`, tokens, API keys, dados industriais confidenciais, bases pessoais ou relatórios proprietários.
- Serviços FastAPI e Streamlit estão preparados para testes locais; implantação pública exige autenticação, TLS, limitação de tráfego, auditoria e autorização.
- Não utilizar previsões sintéticas para aprovar compras, contratar ou rejeitar pessoas, emitir ordens MES/OT ou executar comandos de segurança industrial.
- Verificar dependências, CVEs, direitos de conteúdo e imagens Docker antes de qualquer publicação.
- Pages é somente hospedagem HTML estática; não oferece backend seguro ou banco de dados.

Pacotes GHCR e releases são prévias técnicas, não certificações de segurança ou compliance.
