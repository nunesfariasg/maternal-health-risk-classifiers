"""Gera PDF em diagramação SBC e fonte Markdown a partir dos resultados efetivos."""

import json
from html import escape
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
AUTHORS = [
    "Matheus Emanuel Solda de Oliveira",
    "Matheus Buratto",
    "Luiz Otavio",
    "Gabriel Heinrick Dias",
    "Gustavo Nunes",
]
TITLE = "Comparação de classificadores para risco de saúde materna"


def main():
    results, report = ROOT / "results", ROOT / "report"
    report.mkdir(exist_ok=True)
    scores = pd.read_csv(results / "accuracies.csv")
    summary = pd.read_csv(results / "summary.csv", index_col="classifier")
    audit = json.loads((results / "data_audit.json").read_text(encoding="utf-8"))
    stats = json.loads((results / "statistics.json").read_text(encoding="utf-8"))
    meta = json.loads((results / "metadata.json").read_text(encoding="utf-8"))
    candidates = pd.read_csv(results / "candidates.csv")
    chosen = pd.read_csv(results / "best_params.csv")
    best = summary["mean"].idxmax()
    order = ["KNN", "SVM", "AD", "MLP"]
    body = ParagraphStyle(
        "body",
        fontName="Times-Roman",
        fontSize=12,
        leading=14,
        alignment=TA_JUSTIFY,
        firstLineIndent=1.27 * cm,
        spaceBefore=6,
    )
    heading = ParagraphStyle(
        "heading",
        fontName="Times-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=8,
        keepWithNext=True,
    )
    title = ParagraphStyle(
        "title",
        fontName="Times-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=12,
    )
    centered = ParagraphStyle(
        "centered", parent=body, alignment=TA_CENTER, firstLineIndent=0, spaceAfter=6
    )
    abstract = ParagraphStyle(
        "abstract",
        parent=body,
        fontName="Times-Italic",
        firstLineIndent=0,
        leftIndent=0.8 * cm,
        rightIndent=0.8 * cm,
    )
    small = ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=12)
    story, markdown = [], [f"# {TITLE}", ", ".join(AUTHORS)]

    def p(text, style=body):
        story.append(Paragraph(escape(text), style))
        markdown.append(text + "\n")

    def h(text):
        p(text, heading)
        markdown[-1] = "## " + markdown[-1]

    def table(rows, widths=None):
        cells = [[Paragraph(escape(str(c)), small) for c in row] for row in rows]
        t = Table(cells, colWidths=widths, repeatRows=1, hAlign="CENTER")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8edf0")),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                    ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([t, Spacer(1, 6)])
        markdown.extend(
            [
                "| " + " | ".join(map(str, rows[0])) + " |",
                "| " + " | ".join(["---"] * len(rows[0])) + " |",
            ]
        )
        markdown.extend("| " + " | ".join(map(str, row)) + " |" for row in rows[1:])
        markdown.append("")

    def page():
        story.append(PageBreak())

    p(TITLE, title)
    p("Matheus Emanuel Solda de Oliveira, Matheus Buratto, Luiz Otavio,", centered)
    p("Gabriel Heinrick Dias, Gustavo Nunes", centered)
    p("Engenharia de Software - Centro Universitário FAG", centered)
    p("Inteligência Artificial - Grupo 2 - 2º Bimestre de 2026", centered)
    p(
        "Abstract. We compare KNN, decision tree, SVM and MLP on the UCI Maternal Health Risk "
        "dataset. Ten stratified 50/25/25 splits separate training, validation and testing. "
        "Exact duplicates are removed and hyperparameters are selected only on validation. "
        f"{best} has the highest observed mean test accuracy ({summary.loc[best, 'mean'] * 100:.2f}%). "
        "Kruskal-Wallis and pairwise Mann-Whitney tests are reported with dependence caveats.",
        abstract,
    )
    p(
        "Resumo. Comparamos KNN, árvore de decisão, SVM e MLP na base Maternal Health Risk "
        "da UCI. Realizamos dez divisões estratificadas 50/25/25, removemos duplicatas exatas "
        "e selecionamos hiperparâmetros somente pela validação. Apresentamos acurácias, "
        "dispersão e testes de Kruskal-Wallis e Mann-Whitney. Os resultados descrevem um "
        "experimento acadêmico com rótulos conflitantes e escores dependentes.",
        abstract,
    )
    h("1. Introdução")
    p(
        "O objetivo desta avaliação é comparar quatro conceitos de classificação sobre os "
        "mesmos dados: vizinhança (KNN), regras hierárquicas (AD), margens de separação "
        "(SVM) e redes neurais (MLP). A variável alvo contém três níveis de risco. A métrica "
        "principal exigida é a acurácia, fração de predições corretas no conjunto de teste."
    )
    p(
        "A calibração em validação e a avaliação posterior no teste separam a escolha de "
        "configurações da estimativa de desempenho. Não desenvolvemos nem validamos uma "
        "ferramenta de decisão clínica; o alcance desta análise é a atividade acadêmica."
    )
    page()
    h("2. Dados e análise exploratória")
    p(
        "Ahmed (2020) disponibiliza dados coletados em hospitais, clínicas comunitárias e "
        "unidades de saúde materna de áreas rurais de Bangladesh, associados a monitoramento "
        "por IoT. A UCI identifica a base pelo id 863 e a distribui sob CC BY 4.0. O arquivo "
        f"contém {audit['raw_rows']} registros e seis atributos numéricos; o portal informa "
        "1.013 registros. Adotamos a contagem verificada no CSV e registramos seu SHA-256."
    )
    table(
        [
            ["Atributo", "Significado / unidade", "Mínimo / máximo no CSV"],
            ["Age", "Idade (anos)", "10 / 70"],
            ["SystolicBP", "Pressão sistólica (mmHg)", "70 / 160"],
            ["DiastolicBP", "Pressão diastólica (mmHg)", "49 / 100"],
            ["BS", "Glicemia (mmol/L)", "6 / 19"],
            ["BodyTemp", "Temperatura (°F)", "98 / 103"],
            ["HeartRate", "Frequência cardíaca (bpm)", "7 / 90"],
        ],
        [86, 205, 134],
    )
    table(
        [["Classe RiskLevel", "CSV original", "Após deduplicação"]]
        + [
            [c, audit["raw_class_counts"][c], audit["used_class_counts"][c]]
            for c in ["low risk", "mid risk", "high risk"]
        ],
        [170, 120, 135],
    )
    p(
        f"Não encontramos ausências. Removemos {audit['exact_duplicates_removed']} linhas "
        f"repetidas considerando os seis atributos e o alvo, restando {audit['rows_used']} "
        "registros. Essa decisão evita distribuir a mesma linha completa entre conjuntos; "
        "também muda a frequência das classes e a população avaliada. Sem identificador de "
        "paciente não é possível provar que cada linha representa uma pessoa diferente."
    )
    p(
        f"Há {audit['conflicting_feature_groups']} vetores de atributos com rótulos distintos. "
        "Mantivemos essas observações sem escolher um rótulo por votação. Mesmo sem linhas "
        "completas repetidas, vetores de atributos iguais podem aparecer em conjuntos diferentes. "
        "As contagens por partição constam em split_audit.json; isso limita a generalização "
        "para perfis clínicos ainda não observados."
    )
    p(
        "Registramos os extremos, inclusive HeartRate=7, sem excluir ou corrigir valores por "
        "suposição clínica. A regra exploratória de 1,5 intervalo interquartil, aplicada ao "
        "CSV original, sinalizou: "
        + "; ".join(f"{k}: {v}" for k, v in audit["raw_iqr_outlier_counts"].items())
        + ". Essas contagens não alteram o pré-processamento."
    )
    page()
    h("3. Protocolo e calibração")
    p(
        "Fixamos as sementes 0 a 9 antes da execução. Em cada repetição, embaralhamos a base, "
        "separamos 50% para treino e dividimos o restante ao meio, usando estratificação "
        "nas duas etapas. Cada divisão contém 226 registros no treino, 113 na validação "
        "e 113 no teste. As proporções das classes têm o arredondamento inevitável das "
        "contagens inteiras. Os quatro algoritmos recebem os mesmos conjuntos."
    )
    p(
        "Embaralhamos o treino novamente antes dos ajustes. KNN, SVM e MLP utilizam um "
        "Pipeline com StandardScaler: calculamos média e escala somente nas 226 linhas do "
        "treino. Validação e teste recebem apenas transform. A AD utiliza os atributos "
        "originais, pois suas divisões não precisam dessa padronização."
    )
    table(
        [
            ["Modelo", "Grade fixa de hiperparâmetros", "Candidatos"],
            ["KNN", "K: 3, 5, 7, 11; pesos: uniform, distance", 8],
            ["AD", "criterion: gini, entropy; ccp_alpha: 0, 0.005, 0.02", 6],
            ["SVM", "C: 0.1, 1, 10; kernel: poly, rbf", 6],
            [
                "MLP",
                (
                    "Épocas: 200, 500; taxa: 0.001, 0.01; camadas: (16), (16,8); "
                    "ativação: identity, logistic, tanh, relu"
                ),
                32,
            ],
        ],
        [48, 313, 64],
    )
    p(
        "A grade reúne alternativas simples e orçamentos de treinamento executáveis, sem "
        "pretensão de busca exaustiva. Na AD, ccp_alpha=0 desativa a poda por complexidade "
        "de custo e os valores positivos a habilitam. No SVM, mantemos degree=3 e gamma=scale. "
        "No MLP, fixamos solver=adam, early_stopping=False, tol=0 e n_iter_no_change=501 "
        "para executar o orçamento de 200 ou 500 épocas; mantemos os demais padrões da "
        "versão instalada. Registramos n_iter_ e avisos para cada candidato."
    )
    p(
        "Ajustamos cada candidato somente no treino e escolhemos a maior acurácia de "
        "validação. Em empate, usamos a primeira combinação na ordem determinística de "
        "ParameterGrid. Retemos o modelo já ajustado, sem novo treino em treino+validação. "
        "Somente após a escolha calculamos suas predições no teste. São 520 ajustes de "
        "candidatos e 40 avaliações finais. Nenhuma grade foi alterada após observar o teste."
    )
    warn_count = int(candidates.warnings.ne("[]").sum())
    p(
        f"O arquivo candidates.csv registra {warn_count} candidatos com avisos. Atingir o "
        "limite de épocas do MLP não garante convergência; com tol=0, o aviso de limite é "
        "esperado e não significa, por si só, treinamento inválido. Não aumentamos o orçamento "
        "em resposta às acurácias do teste."
    )
    page()
    h("4. Resultados no teste")
    rows = [["Repetição", *order]]
    rows += [
        [int(row.repetition), *[f"{row[k] * 100:.2f}" for k in order]]
        for _, row in scores.iterrows()
    ]
    rows += [
        ["Média", *[f"{summary.loc[k, 'mean'] * 100:.2f}" for k in order]],
        ["DP amostral", *[f"{summary.loc[k, 'std'] * 100:.2f}" for k in order]],
    ]
    table(rows, [85] * 5)
    p(
        "Tabela 1. Acurácias em porcentagem. DP: desvio padrão amostral, com divisor n-1.",
        ParagraphStyle("caption", parent=small, alignment=TA_CENTER, spaceAfter=8),
    )
    story.append(Image(str(results / "accuracies.png"), width=415, height=237))
    markdown.append("![Acurácias](../results/accuracies.png)\n")
    ranking = summary.sort_values("mean", ascending=False)
    p(
        "Na ordenação descritiva das médias: "
        + "; ".join(
            f"{name}: {row['mean'] * 100:.2f}% (DP {row['std'] * 100:.2f} p.p.)"
            for name, row in ranking.iterrows()
        )
        + ". A maior média observada depende deste protocolo, das grades e da deduplicação."
    )
    page()
    h("5. Análises estatísticas e comparações individuais")
    kw = stats["kruskal_wallis"]
    p(
        f"Aplicamos Kruskal-Wallis às quatro amostras de dez acurácias: "
        f"H={kw['statistic_h']:.5f}, p={kw['pvalue']:.6g}. Com alpha=0,05, "
        + (
            "rejeitamos a hipótese nula de distribuições iguais."
            if kw["pvalue"] < 0.05
            else "não rejeitamos a hipótese nula; isso não demonstra equivalência entre os modelos."
        )
    )
    p(
        "Executamos Mann-Whitney bilateral nos seis pares. Usamos a aproximação assintótica, "
        "com correção de empates e continuidade da SciPy. Reportamos o p bruto exigido e "
        "p ajustado=min(1,6p) por Bonferroni, cujo limiar equivalente é 0,05/6. O teste "
        "compara distribuições; diferenças de média servem aqui como descrição de direção."
    )
    table(
        [["Par", "U", "p bruto", "p Bonf.", "Sig. Bonf."]]
        + [
            [
                f"{pair['a']} x {pair['b']}",
                f"{pair['statistic_u']:.1f}",
                f"{pair['pvalue']:.5f}",
                f"{pair['p_bonferroni']:.5f}",
                "Sim" if pair["significant_bonferroni"] else "Não",
            ]
            for pair in stats["mann_whitney"]
        ],
        [85] * 5,
    )
    for pair in stats["mann_whitney"]:
        delta = pair["mean_difference_a_minus_b"] * 100
        leader = pair["a"] if delta >= 0 else pair["b"]
        conclusion = (
            "há diferença no teste bruto e após Bonferroni"
            if pair["significant_bonferroni"]
            else "há diferença apenas no teste bruto"
            if pair["significant_raw"]
            else "não há diferença significativa no teste bruto ou ajustado"
        )
        p(
            f"{pair['a']} x {pair['b']}: {leader} teve média {abs(delta):.2f} pontos "
            f"percentuais maior; {conclusion}. A interpretação é exploratória."
        )
    p(
        "O enunciado exige testes concebidos para amostras independentes. Aqui os modelos "
        "compartilham partições e as repetições reutilizam registros da mesma base. Logo, "
        "não atendemos estritamente à independência; os valores de p não sustentam uma "
        "afirmação confirmatória de superioridade. Um estudo posterior deve planejar "
        "inferência pareada e controlar a dependência de reamostragem. Bonferroni não corrige "
        "essa dependência."
    )
    page()
    h("6. Conclusões e reprodução")
    p(
        f"{best} apresentou a maior média de teste neste experimento. O protocolo cumpriu "
        "as dez repetições, as partições estratificadas 50/25/25, a calibração na validação "
        "e a avaliação final separada. Os resultados não estabelecem um algoritmo "
        "universalmente melhor e não estimam desempenho clínico fora desta base."
    )
    p(
        "As principais limitações são a amostra reduzida após deduplicação, a ausência de "
        "identificador de paciente, os vetores com rótulos conflitantes, a retenção de extremos, "
        "as grades finitas e a dependência dos escores nos testes exigidos. Acurácia também "
        "pode ocultar diferenças por classe; salvamos matrizes de confusão e precision, recall "
        "e F1 por classe como material complementar, sem utilizá-los na seleção."
    )
    p("Na semente 0, as configurações escolhidas foram:")
    table(
        [["Modelo", "Hiperparâmetros escolhidos"]]
        + [
            [row.classifier, row.params.replace("model__", "")]
            for _, row in chosen[chosen.seed.eq(0)].iterrows()
        ],
        [48, 377],
    )
    p(
        "O arquivo best_params.csv contém as 40 escolhas; candidates.csv contém os 520 "
        "candidatos e suas acurácias de validação. splits.csv preserva os índices originais "
        "e predictions.csv permite recalcular cada acurácia. O experimento utiliza uma "
        f"thread numérica e Python {meta['python']}; versões: "
        + "; ".join(f"{k} {v}" for k, v in meta["packages"].items())
        + "."
    )
    p(
        "Para reproduzir, instale requirements.txt em ambiente virtual e execute "
        "python -m src.experiment --output results-reproducao. Para regenerar este documento "
        "a partir dos resultados oficiais locais, execute python scripts/build_report.py. "
        "O README descreve a instalação, os testes e o empacotamento."
    )
    h("Referências")
    refs = [
        (
            "Ahmed, M. (2020). Maternal Health Risk [Dataset]. UCI Machine Learning Repository. "
            "https://doi.org/10.24432/C5DP5D. CC BY 4.0. Acesso: 26 nov. 2026."
        ),
        (
            "Scikit-learn. Common pitfalls and recommended practices; MLPClassifier; "
            "User Guide. https://scikit-learn.org/stable/. Acesso: 26 nov. 2026."
        ),
        (
            "SciPy. kruskal e mannwhitneyu, documentação da API. "
            "https://docs.scipy.org/doc/scipy/reference/stats.html. Acesso: 26 nov. 2026."
        ),
        (
            "SBC. Modelo de artigos, reproduzido em material da UFPR: "
            "https://www.inf.ufpr.br/menotti/ci1027-261/slides/t01-latexoverleaf.pdf. "
            "A4, coluna única, Times 12, margens superior 3,5 cm, inferior 2,5 cm e laterais "
            "3 cm. Sem marcação chapter. O link atual da SBC estava indisponível na consulta."
        ),
    ]
    for ref in refs:
        p(ref, ParagraphStyle("ref", parent=body, fontSize=10, leading=12, firstLineIndent=0))
    (report / "relatorio.md").write_text("\n\n".join(markdown), encoding="utf-8")
    doc = SimpleDocTemplate(
        str(report / "relatorio.pdf"),
        pagesize=A4,
        topMargin=3.5 * cm,
        bottomMargin=2.5 * cm,
        leftMargin=3 * cm,
        rightMargin=3 * cm,
        title=TITLE,
        author=", ".join(AUTHORS),
    )
    doc.build(story)
    print("Relatório gerado em report/relatorio.pdf e report/relatorio.md")


if __name__ == "__main__":
    main()
