# ==============================================================================
# Compilador RPN -> ARMv7 Assembly (Fase 1)
# Analisador Léxico com Autômato Finito Determinístico e Gerador de Assembly
#
# Integrantes do grupo (ordem alfabética):
#   - Anabelly Sthephany Paiva Montibeller | nabelly19
#   - Aluno2 Nome Sobrenome (@github_user2)
#   - Camila Vieira de Oliveira | camila-vieirao
#   - Guilherme Ferraz | Guilhermeffda 
#
# Grupo: RA1-16
# Instituição: Pontifícia Universidade Católica do Paraná
# ==============================================================================

import sys
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

    # Etapa de verificação de argumentos da linha de comando
    if len(sys.argv) < 2:
        print("Uso: python compilador.py <arquivo_teste> [--testes]")
        print("  <arquivo_teste>  : arquivo com expressoes RPN")
        print("  --testes         : executa testes automatizados")
        sys.exit(1)

    arquivo = sys.argv[1]

    print(f"[INFO] Lendo arquivo: {arquivo}")

    # 2o Leitura do arquivo
    linhas = lerArquivo(arquivo)

    if not linhas:
        print("[ERRO] Arquivo vazio ou não encontrado.")
        sys.exit(1)

    # Reset do estado do assembly
    reset_state()

    tokens_por_linha = []

    # 3o Análise léxica (parte do aluno1)
    for i, linha in enumerate(linhas):
        tokens = []
        parseExpressao(linha.strip(), tokens)
        tokens_por_linha.append(tokens)

    # 4o Execução lógica (parte do aluno2)
    resultados = executarExpressao(tokens_por_linha)

    # 5o Geração de assembly (parte do aluno3)
    codigo_assembly = ""

    for tokens in tokens_por_linha:
        gerar_linha_assembly(tokens, codigo_assembly)

    codigo_assembly = build_assembly()

    # 6o Salvar assembly (mandatory)
    with open("output.s", "w") as f:
        f.write(codigo_assembly)

    print("[INFO] Assembly gerado em output.s")

    # 7o Salvar tokens (mandatory)
    with open("tokens.txt", "w") as f:
        for linha in tokens_por_linha:
            f.write(" ".join(linha) + "\n")
    
    print("[INFO] Tokens salvos em tokens.txt")

    # 8o Exibir resultados (parte do aluno4)
    exibirResultados(resultados)

if __name__ == "__main__":
    main()