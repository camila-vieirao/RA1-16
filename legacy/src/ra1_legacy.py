# INTEGRANTES:
# anabelly... | \
# andressa... | \
# Camila Vieira de Oliveira | camila-vieirao
# guilherme... | \
#
# NOME DO GRUPO: RA1-16

import sys
import utils.gerar_assembly


def lerArquivo(file_path: str) -> list:
    linhas = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                linhas.append(line)
    return linhas


def parseExpressao(linha: str, tokens: list) -> None:
    pass  # Aluno 1


def executarExpressao(tokens: list, resultados: list, memoria: dict) -> None:
    pass  # Aluno 2


def gerarAssembly(tokens: list, codigoAssembly: list) -> None:
    utils.gerar_assembly.gerar_linha_assembly(tokens, codigoAssembly)


def exibirResultados(resultados: list) -> None:
    pass  # Aluno 4


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo_entrada>")
        sys.exit(1)

    arquivo = sys.argv[1]
    utils.gerar_assembly.reset_state()

    resultados, memoria, codigoAssembly = [], {}, []

    linhas = [("3.14 2.0 +"), ("10.0 5.5 -"), ("3.0 4.0 *"), ("7.0 2.0 /"), ("7 2 //"), ("7 3 %"), ("2.0 3 ^"), ("42.5 VAL"), ("VAL"), ("1 RES"), ("(3.0 4.0 *) (2.0 5.0 *) +"), ("2 RES")]
    tokens = [
        ["(", "3.14", "2.0", "+", ")"],
        ["(", "10.0", "5.5", "-", ")"],
        ["(", "3.0", "4.0", "*", ")"],
        ["(", "7.0", "2.0", "/", ")"],
        ["(", "7", "2", "//", ")"],
        ["(", "7", "3", "%", ")"],
        ["(", "2.0", "3", "^", ")"],
        ["(", "42.5", "VAL", ")"],
        ["(", "VAL", ")"],
        ["(", "1", "RES", ")"],
        ["(", "(", "3.0", "4.0", "*", ")", "(", "2.0", "5.0", "*", ")", "+", ")"],
        ["(", "2", "RES", ")"],
    ]
    utils.gerar_assembly.reset_state()

    for token in tokens:
        executarExpressao(token, resultados, memoria)
        gerarAssembly(token, codigoAssembly)

    # =============== ESSE VAI SER O MAIN REAL, EM CIMA TÁ ASSIM PQ AINDA NAO TEM AS LINHAS PROCESSADAS PRA LER ================
    #linhas = lerArquivo(arquivo)
    #
    #resultados, memoria, codigoAssembly = [], {}, []

    #for linha in linhas:
    #    tokens = []
    #    parseExpressao(linha, tokens)
    #    executarExpressao(tokens, resultados, memoria)
    #    gerarAssembly(tokens, codigoAssembly)

    #exibirResultados(resultados)
    # ==========================================================================================================================

    saida = arquivo.rsplit(".", 1)[0] + ".s"
    with open(saida, "w") as f:
        f.write(utils.gerar_assembly.build_assembly())
    print(f"Assembly gerado: {saida}")
