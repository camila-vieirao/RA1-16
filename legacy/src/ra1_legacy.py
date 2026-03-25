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



def executarExpressao(tokens, resultados, memoria):
    """
    Avalia uma expressão usando uma pilha.
    Adaptado para o formato de tokens do projeto (lista de strings).
    """

    pos_ref = [0]

    def _avaliar(tokens, pos_ref, resultados, memoria):
        if pos_ref[0] >= len(tokens):
            return None

        token = tokens[pos_ref[0]]

        # Número
        try:
            valor = float(token)
            pos_ref[0] += 1
            return valor
        except ValueError:
            pass

        # Parênteses
        if token == "(":
            pos_ref[0] += 1  # pula '('

            # Caso: (VAL)
            if (pos_ref[0] < len(tokens) and tokens[pos_ref[0]] == "VAL"
                and pos_ref[0] + 1 < len(tokens) and tokens[pos_ref[0] + 1] == ")"):
                
                pos_ref[0] += 2
                return memoria.get("VAL", 0.0)

            # Caso: (N RES)
            if (pos_ref[0] < len(tokens) and
                pos_ref[0] + 2 < len(tokens) and
                tokens[pos_ref[0] + 1] == "RES"):
                
                n = int(float(tokens[pos_ref[0]]))
                pos_ref[0] += 2
                pos_ref[0] += 1  # pula ')'

                indice = len(resultados) - n
                if 0 <= indice < len(resultados):
                    return resultados[indice]
                else:
                    print(f"AVISO: RES({n}) fora do alcance")
                    return 0.0

            # Primeiro operando
            a = _avaliar(tokens, pos_ref, resultados, memoria)
            if a is None:
                return None

            # Caso: (V VAL) -> salva na memória
            if pos_ref[0] < len(tokens) and tokens[pos_ref[0]] == "VAL":
                pos_ref[0] += 1  # VAL
                pos_ref[0] += 1  # ')'
                memoria["VAL"] = a
                return a

            # Segundo operando
            b = _avaliar(tokens, pos_ref, resultados, memoria)
            if b is None:
                return None

            # Operador
            if pos_ref[0] >= len(tokens):
                return None

            op = tokens[pos_ref[0]]
            pos_ref[0] += 1  # operador
            pos_ref[0] += 1  # ')'

            # Operações
            if op == '+':
                return a + b
            elif op == '-':
                return a - b
            elif op == '*':
                return a * b
            elif op == '/':
                if b == 0:
                    print("AVISO: divisão por zero")
                    return float('inf')
                return a / b
            elif op == '//':
                if b == 0:
                    print("AVISO: divisão inteira por zero")
                    return 0.0
                return float(int(a) // int(b))
            elif op == '%':
                if b == 0:
                    print("AVISO: módulo por zero")
                    return 0.0
                return float(int(a) % int(b))
            elif op == '^':
                resultado = 1.0
                for _ in range(int(b)):
                    resultado *= a
                return resultado
            else:
                print(f"ERRO: operador desconhecido '{op}'")
                return None

        return None

    resultado = _avaliar(tokens, pos_ref, resultados, memoria)

    if resultado is not None:
        resultados.append(resultado)


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
