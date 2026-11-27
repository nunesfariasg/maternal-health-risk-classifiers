# Plano e registro da atividade

Objetivo: executar o protocolo do README e entregar resultados auditáveis, relatório PDF,
código em ZIP e roteiro de 20 minutos. Especificação: README, seções 3 a 12.
Implementação local autorizada pela solicitação; push e PR ficam para a próxima etapa.

1. `src/data.py`, `tests/test_data.py`: carregar o CSV oficial, auditar duplicatas,
   conflitos de rótulo, ausências e extremos; remover repetições exatas; dividir
   50/25/25 com estratificação e sementes 0 a 9. Verificar exclusividade e proporções.
2. `src/models.py`, `tests/test_models.py`: grades fixadas antes do teste, Pipeline
   com StandardScaler apenas no treino; seleção por validação e desempate pela
   primeira combinação da ParameterGrid. Testar ausência de vazamento e escolha.
3. `src/experiment.py`, `src/stats.py`, `tests/test_stats.py`: dez execuções completas,
   CSVs de candidatos, parâmetros, divisões e predições; médias/DP amostral,
   Kruskal-Wallis e seis Mann-Whitney bilaterais, com Bonferroni adicional.
4. `scripts/build_report.py`, `scripts/package_delivery.py`, `report/`, `results/`:
   relatório derivado dos resultados reais, gráficos, roteiro e ZIP; conferir
   PDF visualmente e testar o código extraído do ZIP.

Critério de aceite: 40 avaliações finais, dez por algoritmo; todas as dimensões de
hiperparâmetros exigidas; nenhum fit em validação/teste; todos os resultados e
decisões rastreáveis. Python 3.14 em ambiente virtual, dependências fixadas após instalar.
Sem remoção clínica de extremos sem evidência. Não há aplicação clínica ou serviço remoto.

Riscos a discutir: arredondamento das proporções para tamanho ímpar; vetores iguais
com rótulos distintos; dependência entre escores das mesmas partições e sobreposição
entre repetições; convergência do MLP e alcance limitado das grades.

## Progresso

- Repositório clonado, apenas README na origem; branch `feat/experimento-classificadores`.
- Não havia testes ou dependências preexistentes.
- Etapas 1 e 2 concluídas: auditoria de 1.014 linhas, 562 duplicatas removidas,
  452 linhas usadas; partições e seleção protegidas por testes.
- Etapa 3 concluída: 520 candidatos, 40 avaliações finais; médias, DP amostral,
  Kruskal-Wallis e seis Mann-Whitney. Resultados rastreados por hashes dos fontes.
- Etapa 4: PDF de seis páginas gerado e revisado visualmente; fonte Markdown,
  roteiro e ZIP disponíveis. Conferência em ambiente limpo registrada em VALIDACAO.md.
- 18 testes aprovados; lint e formatação aprovados. Sem commit, push ou PR.
