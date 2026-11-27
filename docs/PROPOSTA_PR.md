# Proposta para a próxima PR

Título: `feat: executa comparação de classificadores e gera entrega da avaliação`

O repositório continha apenas o enunciado. Esta implementação executa dez repetições
estratificadas 50/25/25 para KNN, SVM, AD e MLP, seleciona hiperparâmetros somente
na validação e salva os resultados de teste e sua proveniência.

Inclui base oficial com atribuição e hash, auditoria de dados, grades documentadas,
520 avaliações de candidatos, 40 escores finais, testes estatísticos, gráfico,
relatório PDF em diagramação SBC, fonte Markdown, roteiro de 20 minutos e gerador
do ZIP de entrega. A execução completa levou cerca de 106 segundos neste ambiente.

Resultados: AD 68,32%, MLP 68,14%, SVM 67,26% e KNN 66,28% de acurácia média.
Kruskal-Wallis: p=0,62307. Nenhum dos seis Mann-Whitney rejeitou a hipótese nula
a 5%; a ordenação das médias não sustenta superioridade estatística.

## Validação

Consultar `docs/VALIDACAO.md` para comandos reais, resultados e limitações.
Os testes verificam seleção, escalonamento sem vazamento, exclusividade das linhas,
estratificação, estatística, predições e hashes dos fontes usados no experimento.

## Pontos de revisão da equipe

- Confirmar remoção das duplicatas exatas, retenção dos conflitos e das grades.
- Ler a ressalva de independência dos testes estatísticos exigidos pelo enunciado.
- Conferir nomes e formato com o modelo específico da SBC indicado pelo professor.
- Ensaiar a apresentação e entregar PDF e ZIP no Classroom.

Branch local: `feat/experimento-classificadores`. Esta etapa não cria commit, push
ou PR; o documento é a proposta revisável para abrir a PR na etapa seguinte.
