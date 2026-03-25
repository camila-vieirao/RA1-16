import sys
# INTEGRANTES:
# Anabelly Sthephany Paiva Montibeller | nabelly19
# andressa... | \
# Camila Vieira de Oliveira | camila-vieirao
# guilherme... | \
#
# NOME DO GRUPO: RA1-16

from utils.gerar_assembly import (gerar_linha_assembly, build_assembly, reset_state)
from utils.ler_arquivo import lerArquivo
from utils.exibir_resultados import exibirResultados

# Stubs temporários ALUNO 1
def parseExpressao(linha: str, tokens: list) -> None:
    """
    Stub temporário.
    NÃO usar na entrega final.
    """
    temp = linha.replace("(", " ( ").replace(")", " ) ").split()
    tokens.extend(temp)

# Stubs temporários ALUNO 2
def executarExpressao(tokens_por_linha: list) -> list:
    """
    Stub temporário.
    NÃO pode existir na versão final.
    """
    resultados = []

    for tokens in tokens_por_linha:
        try:
            numeros = []
            for t in tokens:
                try:
                    numeros.append(float(t))
                except:
                    pass

            resultados.append(sum(numeros))
        except:
            resultados.append(0.0)

    return resultados

# ==============================================================================
# FUNÇÃO PRINCIPAL (main)
# ==============================================================================

def main():
    """
    Função principal do compilador.
    Gerencia o fluxo de execução:
    1. Lê argumentos da linha de comando
    2. Executa testes se solicitado
    3. Lê o arquivo de entrada
    4. Analisa cada linha (analisador léxico)
    5. Avalia expressões (para validação)
    6. Gera código Assembly
    7. Salva tokens e Assembly em arquivos
    8. Exibe resultados
    """

    # Etapa de VERIFICAÇÃO DE ARGUMENTOS da linha de comando
    if len(sys.argv) < 2:
        print("Uso: python compilador.py <arquivo_teste> [--testes]")
        print("  <arquivo_teste>  : arquivo com expressoes RPN")
        print("  --testes         : executa testes automatizados")
        sys.exit(1)

    ## Implementar execução de testes

    #Obtém o nome do arquivo 
    nome_arquivo = sys.argv[1]
    if nome_arquivo == '--testes':
        if len(sys.argv) > 2:
            nome_arquivo = sys.argv[2]
        else:
            return

    # Passo 1: Leitura do arquivo de entrada
    print(f"\n{'=' * 60}")
    print("Compilador RPN -> Assembly ARMv7")
    print(f"Arquivo de entrada: {nome_arquivo}")
    print(f"{'=' * 60}")

    linhas = []
    if not lerArquivo(nome_arquivo, linhas):
        sys.exit(1)

    print(f"\nLinhas lidas: {len(linhas)}")
    for i, linha in enumerate(linhas):
        print(f"  [{i}] {linha}")

    if not linhas:
        print("[ERRO] Arquivo vazio ou não encontrado.")
        sys.exit(1)

    ## Reset do estado do assembly
    ##reset_state()

    # Passo 2: Análise léxica de cada linha
    print(f"\n{'=' * 60}")
    print("ANALISE LEXICA")
    print(f"{'=' * 60}")

    todas_linhas_tokens = []
    erro_lexico = False

    for i, linha in enumerate(linhas):
        tokens = []
        print(f"\n  Linha {i}: {linha}")
        sucesso = parseExpressao(linha, tokens)
        if sucesso:
            print(f"    Tokens: {tokens}")
            todas_linhas_tokens.append(tokens)
        else:
            print("    ERRO na analise lexica!")
            erro_lexico = True
            todas_linhas_tokens.append([])

    if erro_lexico:
        print("\nAVISO: Erros encontrados na analise lexica.")

    # Passo 3: Execução para validação (parte do aluno2)
    resultados = []
    memoria = {}

    for i, tokens in enumerate(todas_linhas_tokens):
        if not tokens:
            resultados.append(None)
            continue
        resultado = executarExpressao(tokens, resultados, memoria)
        resultados.append(resultado)
        if resultado is not None:
            print(f"  Linha {i}: resultado = {resultado}")
        else:
            print(f"  Linha {i}: ERRO na execucao")

    # Passo 4: Exibe resultados
    exibirResultados(resultados)

    # Passo 5: Geração de assembly (parte do aluno3)
    print(f"\n{'=' * 60}")
    print("GERACAO DE ASSEMBLY ARMv7")
    print(f"{'=' * 60}")

    codigo_assembly = []
    ##gerarAssembly(todas_linhas_tokens, codigo_assembly)

    #Relacionar com salvamento do assembly em arquivo (gerarAssembly)

    # Passo 6: Salvar tokens em arquivo
    nome_tokens = "tokens.txt"
    # implementar save de tokens

if __name__ == "__main__":
    main()