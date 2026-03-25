import sys

# ==============================================================================
# FUNÇÃO: lerArquivo
# Realiza a leitura dos arquivos de entrada.
#
# ==============================================================================

def lerArquivo(nome_arquivo, linhas):
    """
    Lê o arquivo de entrada contendo expressões RPN.
    Cada linha não vazia é adicionada à lista de linhas.
    Exibe mensagem de erro caso o arquivo não seja encontrado.
    """
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if linha_limpa:  
                    linhas.append(linha_limpa)
        return True
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{nome_arquivo}' nao encontrado.")
        return False
    except IOError as e:
        print(f"ERRO: Nao foi possivel ler o arquivo '{nome_arquivo}': {e}")
        return False