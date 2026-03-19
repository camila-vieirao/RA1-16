# INTEGRANTES:
# anabelly... | \
# andressa... | \
# Camila Vieira de Oliveira | camila-vieirao
# guilherme... | \
#
# NOME DO GRUPO: RA1-16

def lerArquivo(file_path: str) -> list:
    """
    Lê o arquivo de entrada e armazena as expressões para processamento.

    Args: 
        file_path (str): Caminho do arquivo de entrada.
    Returns:
        list: vetor de linhas
    """
    linhas = []
    for line in open(file_path, 'r'):
        print(line)
        linhas.append(line)
    return linhas

def parseExpressao():
    pass

def executarExpressao():
    pass

def gerarAssembly():
    pass

def exibirResultados():
    pass

if __name__ == "__main__":
    import sys
    arquivo = sys.argv[1]
    lerArquivo(arquivo)

#     parseExpressao()
#     executarExpressao()
#     exibirResultados()
#
