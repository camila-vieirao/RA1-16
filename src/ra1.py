# INTEGRANTES:
# Anabelly Sthephany Paiva Montibeller | nabelly19
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
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            #print(line)
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
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo_entrada>")
        sys.exit(1)
    arquivo = sys.argv[1]
    lerArquivo(arquivo)

#     parseExpressao()
#     executarExpressao()
#     exibirResultados()
#
