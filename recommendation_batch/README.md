# Automotive & Industrial Recommendation Batch #051–#060

**Executável com Pandas, NumPy, Scikit-learn e Streamlit.** Os catálogos, perfis, rotas, notícias, estoques e cenários de compras são inteiramente **artificiais e versionados** em `fixtures.json`. Nenhum sistema SAP, Ariba, frota real ou ERP está conectado; não há impacto empresarial medido.

| ID | Motor executado | Regras de negócio |
|---|---|---|
| 051 | TF-IDF / similaridade cosseno de playbooks e vídeos | Ativo, idioma, somente mídia aprovada |
| 052 | FFT, RMS, energia espectral e sklearn NearestNeighbors | Referências acústicas sintéticas |
| 053 | TF-IDF documental | Revisão vigente, autorização, domínio |
| 054 | Similaridade textual para peças e ferramentas | Compatibilidade, aprovação, estoque mínimo |
| 055 | Ranking iterativo de cursos | Pré-requisitos, habilidade já obtida, orçamento de horas |
| 056 | Cobertura mensurável de skills de perfis fictícios | Disponibilidade e autorização do projeto |
| 057 | TF-IDF combinado à recência | Somente artigos artificiais publicados na fixture |
| 058 | Ranking ponderado de preço/OTIF/qualidade | Aprovação, certificado, capacidade, prazo |
| 059 | Enumeração exaustiva de rotas simples e objetivo multicritério | Carrier aprovado, modal e limites do grafo |
| 060 | Explosão recursiva de BOM, disponibilidade e múltiplos de embalagem | Não omite itens pelo top-K; não emite pedidos |

## Instalação
```bash
python -m pip install -r requirements/recommendation.txt
python -m unittest discover -s tests -p test_recommendation_batch.py -v
python -m recommendation_batch.engine 51 --query "bearing vibration pump" --save
python -m recommendation_batch.engine 59 --query "Pindamonhangaba>Santos" --filters-json '{"modes":["truck","rail"]}'
python -m recommendation_batch.engine 60 --query PUMP-100 --filters-json '{"units":2,"pack_size":5}' --save
python -m streamlit run recommendation_batch/app.py
```

Cada projeto `projetos/06-recommendation/<slug>/main.py` aceita `--query`, `--top-k`, `--filters-json` e `--save`. Sua interface específica é executável via `python -m streamlit run projetos/06-recommendation/<slug>/streamlit_app.py`.

## Avaliação e limites
As evidências disponíveis são **testes de regras, determinismo, exclusões, integridade do BOM, restrições de fornecedores, FFT e rotas artificiais**. Similaridade lexical não equivale a compreensão técnica e as assinaturas FFT foram criadas por fórmulas de laboratório. As métricas de oferta, lead time, emissions e notícias são inventadas para os cenários; não representam trajetos, cotações ou fatos verdadeiros. Não houve avaliação offline com relevância anotada por especialistas (Precision@K/NDCG), A/B test, deployment, monitoramento de drift, autorização de RH ou homologação com sistemas produtivos. #056 não pode decidir alocação profissional sem revisão humana. #058 não substitui homologação e #059 não calcula trajetos rodoviários reais. #060 não equivale a plano de manutenção validado.

Os scripts e o app não geram ordens de compra, não realizam solicitações externas e não alteram registros corporativos.
