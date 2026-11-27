# Validação da entrega

Ambiente: Windows 11, Python 3.14.6, versões fixadas em `requirements.txt`.
Data local: 26/11/2026. Branch: `feat/experimento-classificadores`.

| Verificação | Resultado observado |
| --- | --- |
| `python -m pytest -q` | Aprovado: 18 testes, incluindo resultados reais e proveniência |
| `ruff check src tests scripts` | Aprovado: All checks passed |
| `ruff format --check src tests scripts` | Aprovado: 11 arquivos formatados |
| `python -m src.experiment --output results` | Aprovado: dez sementes, 520 candidatos, 40 avaliações; cerca de 106 s |
| Conferência das predições | Aprovado: os 40 escores correspondem às 4.520 predições salvas |
| Conferência das escolhas | Aprovado: máximo na validação, desempate pelo primeiro candidato |
| Partições | Aprovado: 226/113/113, todos os IDs presentes uma vez por semente, proporções com arredondamento |
| MLP | Aprovado: n_iter_ corresponde às 200 ou 500 épocas de cada candidato; 320 avisos de limite registrados |
| Normalização | Aprovado: teste com distribuição externa deslocada demonstra fit somente no treino |
| Estatística | Aprovado: médias/DP, Kruskal-Wallis e seis Mann-Whitney + Bonferroni |
| `python scripts/build_report.py` | Aprovado: PDF de seis páginas e fonte Markdown |
| Renderização e revisão visual do PDF | Aprovado: seis páginas renderizadas com PyMuPDF, sem cortes ou sobreposições observados |
| Fonte dos dados | Aprovado: CSV UCI original incluído, atribuição CC BY 4.0 e SHA-256 conferido |
| ZIP e ambiente limpo | Aprovado: integridade ZIP, 38 arquivos, sem `.venv`, `.git`, temporários ou caches; instalação em segundo ambiente e 18 testes aprovados a partir da extração |
| Reexecução completa a partir do ZIP | Aprovado: dez sementes novamente; igualdade exata de seis CSVs (`accuracies`, `summary`, `best_params`, `candidates`, `splits`, `predictions`) e do JSON estatístico |
| Nomes dos integrantes | Conferir com a equipe; o README fornece `Luiz Otavio` sem identificação adicional de sobrenome |
| Modelo específico do professor | Pendente: link atual da SBC indisponível; conferir com o arquivo fornecido na disciplina |
| Ensaio e domínio individual | Não executado: ação dos cinco integrantes; roteiro disponível |
| Entrega no Classroom | Não executado: submissão humana |
| Commit, push e PR | Não executado: reservados para a próxima etapa solicitada |

## Falhas encontradas e corrigidas

A coleta inicial falhou pela ausência dos módulos, antes da implementação. Após
implementar, os 13 casos iniciais passaram. A primeira tentativa de experimento
parou ao serializar `SVC.n_iter_` (array NumPy). Um teste de regressão reproduziu a
falha; a conversão para lista corrigiu o problema, e a suíte passou com 14 casos.
Os quatro testes de artefatos reais elevaram o total para 18 aprovados.

O sandbox bloqueou o runtime instalado e o acesso inicial à rede/cache. Usamos
execução autorizada fora do sandbox para preparar e usar o ambiente. Uma tentativa
de mover a saída parcial falhou por ausência do diretório temporário; criamos o
diretório, preservamos a tentativa e executamos o experimento completo em saída nova.
Nenhum resultado parcial integra `results/`.

## Limitações do alcance

As linhas completas são exclusivas entre conjuntos, mas atributos iguais com alvos
conflitantes podem atravessar partições. O relatório e `split_audit.json` deixam isso
explícito. Não há identificação de pacientes. Os escores compartilham dados entre
repetições, portanto os testes exigidos não satisfazem independência estrita.
Não alteramos o protocolo para tentar obter significância.

Não foram necessários testes de navegador, autenticação, RLS ou deploy: não há
aplicação web ou serviço remoto. Codex Security não foi executado; esta entrega
não é um scan de segurança nem uma validação clínica. Não há segredos ou `.env`
necessários ao experimento. O empacotador inclui somente caminhos definidos.
Não testamos outros sistemas operacionais ou versões de Python.
