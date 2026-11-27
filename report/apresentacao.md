# Apresentação e arguição: 20 minutos

Material: `relatorio.pdf`, `results/accuracies.png`, CSVs e código local.
Nenhum download, serviço de nuvem ou execução de IA é necessário durante a fala.
Todos devem estudar o protocolo completo; a divisão abaixo organiza apenas a fala.

| Tempo | Responsável sugerido | Conteúdo e demonstração |
| --- | --- | --- |
| 0–3 min | Matheus Emanuel Solda de Oliveira | Objetivo da avaliação; três classes de risco; acurácia; quatro conceitos de classificação. Abrir a primeira página do relatório. |
| 3–7 min | Matheus Buratto | Seis atributos, origem UCI e licença; 1.014 linhas; 562 duplicatas; 452 linhas usadas; 35 perfis com rótulos conflitantes. Mostrar `data_audit.json` e explicar a decisão de manter extremos. |
| 7–11 min | Luiz Otavio | Sementes 0 a 9; 226/113/113; estratificação e índices exclusivos; scaler só no treino. Mostrar `src/data.py`, Pipeline e um conjunto de índices em `splits.csv`. |
| 11–15 min | Gabriel Heinrick Dias | Grades e calibração: 8 KNN, 6 SVM, 6 AD, 32 MLP; 520 ajustes; seleção só na validação; teste após a escolha. Mostrar `best_params.csv` e as dez linhas de `accuracies.csv`. |
| 15–18 min | Gustavo Nunes | AD 68,32%, MLP 68,14%, SVM 67,26%, KNN 66,28%; DP; Kruskal-Wallis p=0,62307; seis Mann-Whitney sem rejeição. Explicar Bonferroni, dependência e conclusões limitadas. |
| 18–20 min | Todos | Arguição. Cada integrante deve explicar uma decisão metodológica sem depender do responsável por aquele trecho. |

## Explicações que o grupo deve dominar

- **Por que 50/25/25?** É a regra da atividade. Treino ajusta os parâmetros internos,
  validação escolhe os hiperparâmetros e teste estima o desempenho após a escolha.
- **Por que normalizar só no treino?** Ajustar média e escala com validação ou teste
  incorpora informação externa ao treinamento e contamina a comparação.
- **Por que remover 562 linhas?** Para impedir repetição exata da mesma linha em
  conjuntos diferentes. Não sabemos se as multiplicidades representam pessoas
  diferentes; a decisão muda a população avaliada e está documentada.
- **Os conjuntos são exclusivos?** Os IDs de linhas são exclusivos. Vetores iguais
  com rótulos distintos ainda podem ocorrer entre conjuntos; não ocultamos isso.
- **Como escolhemos o melhor candidato?** Maior acurácia de validação. Em empate,
  primeira combinação na ordem determinística de ParameterGrid. Nunca pelo teste.
- **O modelo escolhido aprende com a validação?** Não. Retemos o modelo ajustado
  apenas no treino, sem refit em treino+validação.
- **Qual a diferença entre poda e critério na AD?** Gini/entropia medem a divisão;
  ccp_alpha controla poda por complexidade de custo, sendo zero a opção sem poda.
- **Épocas de MLP significam convergência?** Não. Executamos 200 ou 500 épocas
  completas e registramos o aviso de limite; isso fixa orçamento, não convergência.
- **AD venceu?** Teve a maior média observada, mas os testes não detectaram diferença
  significativa. Não rejeitar H0 não demonstra equivalência nem prova que AD é superior.
- **Por que o cuidado com os p-valores?** Os algoritmos recebem as mesmas partições
  e as dez repetições reutilizam dados. Os testes exigidos assumem independência;
  a análise é exploratória. Bonferroni trata as seis comparações, não essa dependência.
- **O que falta para uso real?** A atividade não valida uso clínico: faltam avaliação
  externa, identificação de pacientes e validação apropriada do domínio.

## Fallback identificado

Se o ambiente Python falhar, apresentar o PDF e os resultados da execução já salva,
identificando-os como resultados reais pré-calculados. Mostrar as dez linhas do CSV,
o hash do arquivo UCI e os metadados. Não simular uma execução ao vivo.

Ensaio: cronometrar 18 minutos de fala e reservar 2 para perguntas; conferir que
todos conseguem explicar as escolhas dos outros. Se o professor reservar a arguição
fora dos 20 minutos, ampliar a leitura das configurações e a discussão por classe.
