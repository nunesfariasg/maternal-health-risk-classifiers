# Avaliação 2º Bimestre — Comparação de Classificadores (Grupo 2)

> **Para assistentes de IA:** este README é o contexto oficial do projeto. Ele resume o enunciado do professor, as restrições obrigatórias, a base de dados do grupo e as decisões de implementação. Ao gerar código, texto do relatório ou explicações, siga as **Regras obrigatórias** abaixo. Idioma de trabalho: **português do Brasil**.

## 1. Informações gerais

| Item | Valor |
|---|---|
| Curso | Engenharia de Software — Centro Universitário FAG |
| Disciplina | Inteligência Artificial |
| Professor | Leandro Ferreira Bueno (leandrobueno@fag.edu.br) |
| Avaliação | 2º Bimestre |
| Data de entrega e apresentação | **27/11/2026** (entrega na tarefa do Classroom) |
| Grupo | **Grupo 2** |
| Base de dados | **Maternal Health Risk** (UCI, id 863) |
| Link da base | https://archive.ics.uci.edu/dataset/863/maternal+health+risk |

### Integrantes
- Matheus Emanuel Solda de Oliveira
- Matheus Buratto
- Luiz Otavio
- Gabriel Heinrick Dias
- Gustavo Nunes

> Todos os integrantes devem ser identificados no relatório.

## 2. Objetivo

Comparar, em termos de **acurácia**, classificadores baseados em conceitos diferentes sobre a **mesma base de dados**:

- **KNN** (K Vizinhos Mais Próximos)
- **AD** (Árvore de Decisão)
- **SVM** (Máquina de Vetor de Suporte)
- **MLP** (Multilayer Perceptron)

A comparação usa a **média de 10 repetições** e é validada com testes estatísticos (Kruskal-Wallis e Mann-Whitney).

## 3. Regras obrigatórias (enunciado)

1. **10 repetições** completas do processo. Os valores comparados são as **médias** das 10 execuções.
2. **Divisão em 3 conjuntos mutuamente exclusivos** (nenhuma instância em mais de um conjunto):
   - Treino: **50%**
   - Validação: **25%**
   - Teste: **25%**
3. **Estratificação:** manter a proporção original das classes em cada conjunto (ex.: 200 de A e 100 de B → treino com 100 de A e 50 de B).
4. **Aleatoriedade total** na escolha das instâncias de cada conjunto.
5. **Embaralhar** os dados antes de dividir e antes de treinar.
6. **Ajuste de hiperparâmetros usando a validação:** treinar no conjunto de treino, variar os parâmetros, medir a acurácia na **validação** e escolher o melhor. O **teste só é usado com o melhor modelo já definido**.
7. Guardar a **acurácia no teste de cada classificador em cada uma das 10 execuções**.
8. Rodar **Kruskal-Wallis** (há diferença entre os algoritmos?) e **Mann-Whitney** comparando os classificadores **dois a dois** (quem é melhor?).
9. Não é preciso implementar os algoritmos: usar **implementações prontas** (o grupo implementa o framework, a análise dos parâmetros e dos resultados).

## 4. Hiperparâmetros exigidos por classificador

| Classificador | Parâmetros a variar | Equivalente no scikit-learn |
|---|---|---|
| **KNN** | Valor de K; pesos dos votos (uniforme e por distância) | `n_neighbors`, `weights='uniform'/'distance'` |
| **AD** | Com poda ou sem poda; critério de divisão (Gini e entropia) | `ccp_alpha` (0 = sem poda, >0 = com poda) ou `max_depth`/`min_samples_leaf`; `criterion='gini'/'entropy'` |
| **SVM** | Valor do erro C; tipo de kernel (polinomial ou radial) | `C`, `kernel='poly'/'rbf'` |
| **MLP** | Nº de épocas; taxa de aprendizagem; nº de camadas escondidas; função de ativação (identidade, logística sigmoide, tangente hiperbólica, ReLU) | `max_iter`, `learning_rate_init`, `hidden_layer_sizes`, `activation='identity'/'logistic'/'tanh'/'relu'` |

> A definição exata das grades de valores (ex.: quais valores de K ou C) é decisão do grupo e deve ser documentada no relatório. Registrar a grade final na seção 8.

## 5. Base de dados: Maternal Health Risk

Dados de saúde materna coletados em hospitais, clínicas comunitárias e unidades de saúde materna de áreas rurais de Bangladesh, via sistema de monitoramento de risco baseado em IoT. O objetivo é classificar o **nível de risco da gestante**.

- **Tarefa:** classificação multiclasse
- **Instâncias:** ≈ 1014 (confirmar ao carregar)
- **Atributos (6, todos numéricos):**

| Atributo | Significado |
|---|---|
| `Age` | Idade (anos) |
| `SystolicBP` | Pressão arterial sistólica (mmHg) |
| `DiastolicBP` | Pressão arterial diastólica (mmHg) |
| `BS` | Glicemia (mmol/L) |
| `BodyTemp` | Temperatura corporal (°F) |
| `HeartRate` | Frequência cardíaca (bpm) |

- **Classe alvo:** `RiskLevel`, com **3 classes**: `low risk`, `mid risk`, `high risk` (classes levemente desbalanceadas, por isso a estratificação é essencial).

### Pontos de atenção na base (verificar e documentar)
- **Possíveis linhas duplicadas.** Duplicatas podem cair em conjuntos diferentes e inflar a acurácia (vazamento). Verificar com `df.duplicated().sum()` e decidir (remover ou manter) **justificando no relatório**.
- **Possíveis outliers** (ex.: idade ou frequência cardíaca com valores atípicos). Verificar antes de decidir qualquer tratamento.
- **Escalas diferentes** entre atributos: KNN, SVM e MLP são sensíveis a isso (ver seção 6).

## 6. Pipeline

Para cada uma das **10 repetições** (uma semente aleatória diferente por repetição):

1. Embaralhar a base.
2. Dividir de forma **estratificada** em 50% treino / 25% validação / 25% teste. Com scikit-learn, em duas etapas:
   - `train_test_split(X, y, train_size=0.5, stratify=y, shuffle=True, random_state=seed)`
   - o restante (50%) é dividido ao meio com `train_test_split(..., test_size=0.5, stratify=...)` para gerar validação e teste.
3. **Normalizar** os atributos (ex.: `StandardScaler`) **ajustando (`fit`) apenas no treino** e aplicando (`transform`) em validação e teste. Nunca ajustar no conjunto completo.
4. Para cada classificador:
   1. Treinar no **treino** para cada combinação de parâmetros da grade.
   2. Medir a acurácia na **validação**.
   3. Escolher a combinação de **maior acurácia de validação**.
   4. Medir a acurácia do melhor modelo no **teste** e guardar.
5. Ao final das 10 repetições, montar a tabela de acurácias (seção 7) e calcular **média e desvio padrão**.
6. Rodar **Kruskal-Wallis** sobre as 4 amostras de 10 acurácias.
7. Rodar **Mann-Whitney** em todos os pares (6 comparações: KNN×AD, KNN×SVM, KNN×MLP, AD×SVM, AD×MLP, SVM×MLP).

### Testes estatísticos
- `scipy.stats.kruskal(knn, ad, svm, mlp)` — H0: não há diferença entre os desempenhos.
- `scipy.stats.mannwhitneyu(a, b, alternative='two-sided')` para cada par; usar médias/medianas para dizer quem foi melhor quando p < α.
- Nível de significância sugerido: α = 0,05. Opcionalmente mencionar correção de múltiplas comparações (ex.: Bonferroni, α/6) como discussão.

## 7. Formato esperado da tabela de resultados (relatório)

| Repetição | KNN | SVM | AD | MLP |
|---|---|---|---|---|
| 1 | Acc | Acc | Acc | Acc |
| 2 | Acc | Acc | Acc | Acc |
| … | … | … | … | … |
| 10 | Acc | Acc | Acc | Acc |
| **Média / DP** | Média / DP | Média / DP | Média / DP | Média / DP |

## 8. Decisões do grupo (preencher conforme o trabalho avança)

- **Linguagem/tecnologias:** Python + scikit-learn, pandas, numpy, scipy, matplotlib/seaborn (confirmar).
- **Tratamento de duplicatas:** _a definir_
- **Normalização:** _a definir_ (sugestão: `StandardScaler`, ajustado só no treino)
- **Grade KNN:** _a definir_
- **Grade AD:** _a definir_
- **Grade SVM:** _a definir_
- **Grade MLP:** _a definir_
- **Sementes:** _a definir_ (sugestão: seeds 0 a 9, registradas para reprodutibilidade)

## 9. Estrutura sugerida do repositório

```
.
├── README.md
├── requirements.txt
├── data/                     # base baixada (ou carregada via ucimlrepo)
├── src/
│   ├── data.py               # carregamento + divisão estratificada 50/25/25
│   ├── models.py             # grades de parâmetros e treino de KNN, AD, SVM, MLP
│   ├── experiment.py         # loop das 10 repetições
│   └── stats.py              # Kruskal-Wallis e Mann-Whitney
├── notebooks/                # exploração e análise
├── results/                  # CSVs de acurácias e gráficos
└── report/                   # relatório no formato SBC
```

Carregamento da base (exemplo):

```python
from ucimlrepo import fetch_ucirepo

maternal = fetch_ucirepo(id=863)
X = maternal.data.features
y = maternal.data.targets.squeeze()
```

## 10. Entregáveis

### 10.1 Relatório (PDF, formato SBC)
Deve conter:
- Descrição dos dados (significado, atributos, classes, número de classes etc.)
- Parâmetros usados na calibração dos modelos
- Tecnologias utilizadas
- Tabela de acurácias por repetição (seção 7) com média e desvio padrão
- Comparação individual entre cada modelo
- Análises estatísticas (Kruskal-Wallis e Mann-Whitney) indicando se há diferença significativa
- Conclusões
- Identificação de todos os integrantes
- Texto claro, explicando cada processo e cada etapa

Formato: modelo de publicações da SBC (https://www.sbc.org.br/documentosinstitucionais/#publicacoes), **excluindo a marcação de capítulo (chapter)** do arquivo do link.

### 10.2 Código
- Todos os arquivos compactados em **um único `.zip`**
- Nome no padrão `NomeSobrenome1-NomeSobrenome2-NomeSobrenome3-NomeSobrenome4-NomeSobrenome5.zip` (o grupo tem 5 integrantes)
- **Não compartilhar link** dos arquivos de código (entregar o zip)

### 10.3 Apresentação
- Formato livre, **20 minutos** de apresentação e arguição
- Foco em: descrição do problema, desempenhos obtidos e resultado da análise estatística
- Não precisa entregar o arquivo da apresentação
- A avaliação da apresentação é **individual**: todos devem dominar o trabalho inteiro

## 11. Checklist

- [ ] Base carregada e explorada (duplicatas, outliers, distribuição das classes)
- [ ] Divisão estratificada 50/25/25, embaralhada e aleatória
- [ ] Normalização ajustada apenas no treino
- [ ] Grades de hiperparâmetros definidas para KNN, AD, SVM e MLP
- [ ] Seleção de parâmetros feita **somente** na validação
- [ ] 10 repetições executadas, acurácias de teste salvas
- [ ] Média e DP calculados
- [ ] Kruskal-Wallis executado
- [ ] Mann-Whitney em todos os pares executado
- [ ] Relatório SBC em PDF (com todos os integrantes)
- [ ] Zip do código com o nome no padrão correto
- [ ] Apresentação de 20 min preparada
- [ ] Entrega no Classroom até **27/11/2026**

## 12. Instruções para assistentes de IA

- Responda e comente o código em **português do Brasil**.
- Use **scikit-learn** (implementações prontas), conforme permitido pelo enunciado.
- **Nunca** use o conjunto de teste para escolher parâmetros e **nunca** ajuste pré-processamento fora do treino.
- Mantenha a **estratificação** e o **embaralhamento** em todas as divisões e use sementes diferentes por repetição.
- Mantenha o código simples e legível: o grupo precisa explicar tudo na arguição individual.
- Ao escrever trechos do relatório, seja claro e explique cada etapa; não invente resultados numéricos: use apenas valores produzidos pelos experimentos.
- Valores marcados como _a definir_ ou "confirmar" ainda não foram decididos ou verificados pelo grupo.
