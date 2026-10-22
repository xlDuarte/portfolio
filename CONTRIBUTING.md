# Guia de contribuições

Este é um portfólio de demonstrações técnicas; as bases auditadas são **sintéticas**. Contribuições devem alinhar escopo anunciado e código realmente executado.

## Processo

1. Consulte [instalação](docs/GETTING_STARTED.md), [auditoria](INTEGRATION_AUDIT.md) e [matriz de tecnologias](TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv).
2. Abra issue descrevendo o projeto numerado, bug ou lacuna com reprodução. Sem credenciais, dados reais de empresas ou informações pessoais.
3. Mantenha código, documentação, testes e páginas HTML coerentes.
4. Execute `python scripts/audit_integrated_portfolio.py --check`, `python -m unittest discover -s tests -v` e os testes específicos do domínio.
5. Ao editar links HTML, teste `python -m unittest discover -s tests -p test_pages_release.py -v` e caminhos de URL com `/portfolio/`.

### Critérios
- Bibliotecas usadas **realmente** no projeto citado, não apenas listadas no README da categoria.
- Proveniência dos datasets, splits, limitações e métricas reproduzíveis.
- Sem afirmações de Power BI Desktop executado, GPS F1 oficial, dados SAP reais ou autenticação inexistente.
- Sem publicação de arquivos de propriedade intelectual de terceiros ou segredos.

Contribuições não concedem automaticamente direitos comerciais de redistribuição do código existente.
