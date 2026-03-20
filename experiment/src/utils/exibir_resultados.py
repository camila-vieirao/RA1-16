def exibirResultados(resultados: list[float]) -> None:
    """
    Exibe os resultados das expressões de forma formatada.
    Não realiza cálculos, apenas apresentação.
    """

    print("\n===== RESULTADOS =====")

    for i, valor in enumerate(resultados, start=1):
        try:
            print(f"Linha {i}: {valor:.1f}")
        except:
            print(f"Linha {i}: ERRO")

    print("======================\n")