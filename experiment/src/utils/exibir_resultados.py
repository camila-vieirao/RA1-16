import math

# ==============================================================================
# FUNÇÃO: exibirResultados
# Exibe os resultados das expressões processadas.
#
# Parâmetros:
#   resultados (list) - lista de resultados (float) de cada linha
# ==============================================================================


def  exibirResultados(resultados):
    """
    Exibe os resultados calculados (pelo executarExpressao, para validação).
    Mostra cada resultado com uma casa decimal para números reais.
    """

    print("\n" + "=" * 60)
    print("RESULTADOS (validacao em Python):")
    print("=" * 60)
    for i, res in enumerate(resultados):
        if res is not None:
            # Verifica se é inteiro
            if res == int(res) and not math.isinf(res):
                print(f"  Linha {i}: {int(res)}")
            else:
                print(f"  Linha {i}: {res:.6f}")
        else:
            print(f"  Linha {i}: ERRO")
    print("=" * 60)