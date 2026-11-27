# Instalação, execução e artefatos

Use Python 3.14. O ambiente validado utiliza Python 3.14.6 no Windows; não foi
validado em outras versões ou sistemas. Não há servidor, credenciais, `.env`,
conta de nuvem ou cobrança de API. A execução após instalar é local e offline.

## Preparar o ambiente

Com Python 3.14 e pip disponíveis, na raiz do repositório:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Neste ambiente usamos o uv, pois o Python padrão é 3.15:

```powershell
uv venv --python 3.14 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

No Linux/macOS, substitua `.venv/Scripts/python.exe` por `.venv/bin/python`.
`requirements.txt` fixa o ambiente completo utilizado, incluindo geração e
renderização do PDF, testes e lint. Não é necessário instalar algoritmos à parte.

## Validar e reproduzir

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/ruff.exe check src tests scripts
.venv/Scripts/ruff.exe format --check src tests scripts
.venv/Scripts/python.exe -m src.experiment --output results-reproducao
.venv/Scripts/python.exe scripts/build_report.py
.venv/Scripts/python.exe scripts/package_delivery.py
```

O diretório de saída do experimento precisa ser novo: o programa recusa sobrescrever
resultados. `results/` já contém a execução entregue. Não altere grades depois de
observar o teste. O relatório lê os arquivos em `results/`; para outro estudo,
revise explicitamente a origem dos resultados antes de regenerar o relatório.

Os testes conferem tanto o pipeline quanto os resultados entregues, inclusive
hashes dos fontes. Se modificar `src/`, os testes de proveniência falharão até
que uma nova execução revisada produza metadados compatíveis. A suíte verifica
18 casos, sem refazer a busca inteira. O experimento original levou cerca de
106 segundos neste computador; outro hardware pode ter tempos diferentes.

## O que cada arquivo permite verificar

| Arquivo | Conteúdo |
| --- | --- |
| `results/accuracies.csv` | Dez acurácias de teste por algoritmo |
| `results/summary.csv` | Média, DP amostral, mediana, mínimo e máximo |
| `results/candidates.csv` | 520 candidatos, acurácias de validação, épocas e avisos |
| `results/best_params.csv` | 40 escolhas finais de parâmetros |
| `results/splits.csv` | Índices originais em cada partição e repetição |
| `results/predictions.csv` | 4.520 predições de teste e rótulos reais |
| `results/data_audit.json` | Duplicatas, classes, ausências, extremos e hash do CSV |
| `results/split_audit.json` | Classes por partição e vetores iguais entre partições |
| `results/statistics.json` | Kruskal-Wallis e seis Mann-Whitney, brutos e Bonferroni |
| `results/classification_reports.json` | Métricas por classe e matrizes de confusão |
| `results/metadata.json` | Grades, versões, sementes, duração e hashes dos fontes |
| `results/accuracies.png` | Gráfico das dez acurácias |
| `report/relatorio.pdf` | Relatório em diagramação SBC, sem chapter |
| `report/relatorio.md` | Texto e tabelas editáveis, gerados junto do PDF |
| `report/apresentacao.md` | Roteiro de 20 minutos, perguntas e fallback |
| `dist/*.zip` | Pacote gerado para entrega; ignorado pelo Git |

## Limitações e ações humanas

A deduplicação reduz a amostra e altera as proporções; o resultado não descreve
a base original com suas multiplicidades. Rótulos conflitantes permanecem e
podem produzir vetores iguais entre conjuntos. Não há ID de paciente para provar
independência entre pessoas. Os testes estatísticos exigidos assumem independência
que este desenho não garante. Nenhum p bruto foi menor que 0,05; isso não prova
equivalência dos algoritmos.

O relatório segue dimensões e tipografia do modelo SBC reproduzido pela UFPR.
O link atual da SBC não respondeu; a comparação com o arquivo específico indicado
pelo professor permanece uma revisão humana de formato. Confirmar a grafia dos
nomes conforme o README, revisar as decisões metodológicas e ensaiar a apresentação.
Não houve envio ao Classroom, push, commit ou abertura de PR nesta etapa.
