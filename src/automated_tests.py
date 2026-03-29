# INTEGRANTES:
# Anabelly Sthephany Paiva Montibeller | nabelly19
# Andressa Aparecida Teixeira de Souza | DessaSouza
# Camila Vieira de Oliveira | camila-vieirao
# Guilherme Ferraz | Guilhermeffda 
#
# NOME DO GRUPO: RA1-16

from ra1 import parseExpressao, executarExpressao, lerArquivo, gerarAssembly

def testar_analisador_lexico():
    print("\n" + "=" * 60)
    print("TESTES DO ANALISADOR LEXICO (AFD)")
    print("=" * 60)
    testes_validos = [
        ("(3.14 2.0 +)",           "Soma de reais"),
        ("(10 3 //)",              "Divisao inteira"),
        ("(10 3 %)",               "Resto"),
        ("(2.0 3 ^)",              "Potenciacao"),
        ("(5 RES)",                "Comando RES"),
        ("(10.5 VALOR)",           "Store em VALOR (maiusculas)"),
        ("(VALOR)",                "Recall de VALOR"),
        ("((3.0 4.0 +) 2.0 *)",   "Expressao aninhada"),
        ("(0.5 100.0 /)",          "Divisao real"),
        ("((1.0 2.0 +) (3.0 4.0 *) -)", "Aninhamento duplo"),
    ]
    passou_v = 0
    for entrada, descricao in testes_validos:
        tokens = []
        sucesso = parseExpressao(entrada, tokens)
        if sucesso: passou_v += 1
        print(f"  [{'OK' if sucesso else 'FALHOU'}] Valido: {descricao}")
        print(f"         Entrada: {entrada}")
        print(f"         Tokens:  {tokens}\n")

    testes_invalidos = [
        ("(3.14 2.0 &)",           "Operador invalido '&'"),
        ("(3.14.5 2.0 +)",         "Numero malformado 3.14.5"),
        ("(3,45 2.0 +)",           "Numero malformado 3,45 (virgula)"),
        ("(abc 2.0 +)",            "Letras minusculas como inicio de token"),
        ("(10.5 CONTADOr)",        "Store em CONTADOr (letra minuscula)"),    
        ("(3.14 2.0 +",            "Parentese desbalanceado (falta fechar)"),
        ("3.14 2.0 +)",            "Parentese desbalanceado (falta abrir)"),
        ("((3.14 2.0 +)",          "Parentese desbalanceado (abre 2, fecha 1)"),
        ("(3.14 2.0 +))",          "Parentese desbalanceado (abre 1, fecha 2)"),
    ]
    passou_i = 0
    for entrada, descricao in testes_invalidos:
        tokens = []
        sucesso = parseExpressao(entrada, tokens)
        if not sucesso: passou_i += 1
        print(f"  [{'OK' if not sucesso else 'FALHOU'}] Invalido: {descricao}")
        print(f"         Entrada: {entrada}")
        if sucesso: print("         ATENCAO: Deveria ter detectado erro!")
        print()
    total = len(testes_validos) + len(testes_invalidos)
    print(f"  Resultado: {passou_v + passou_i}/{total} testes passaram")
    print("=" * 60)

def testar_execucao():
    print("\n" + "=" * 60)
    print("TESTES DE EXECUCAO DE EXPRESSOES")
    print("=" * 60)
    testes = [
        ("(3.14 2.0 +)",   5.14,   "Soma"),
        ("(10.5 3.5 -)",   7.0,    "Subtracao"),
        ("(4.0 2.5 *)",    10.0,   "Multiplicacao"),
        ("(9.0 3.0 /)",    3.0,    "Divisao real"),
        ("(10 3 //)",       3.0,   "Divisao inteira"),
        ("(10 3 %)",        1.0,   "Resto"),
        ("(2.0 3 ^)",       8.0,   "Potenciacao"),
    ]
    passou = 0
    resultados = []
    memoria = {}
    for entrada, esperado, descricao in testes:
        tokens = []
        parseExpressao(entrada, tokens)
        resultado = executarExpressao(tokens, resultados, memoria)
        resultados.append(resultado)
        ok = abs(resultado - esperado) < 1e-9
        if ok: passou += 1
        print(f"  [{'OK' if ok else 'FALHOU'}] {descricao}: {entrada} = {resultado} (esperado: {esperado})")
    print(f"\n  Resultado: {passou}/{len(testes)} testes passaram")
    print("=" * 60)

def testar_leitura_arquivo():
    print("\n" + "=" * 60)
    print("TESTES DE LEITURA DE ARQUIVO")
    print("=" * 60)
    linhas = []
    sucesso = lerArquivo("arquivo_inexistente.txt", linhas)
    print(f"  [{'OK' if not sucesso else 'FALHOU'}] Arquivo inexistente detectado")
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("(3.14 2.0 +)\n(10.5 3.5 -)\n\n(4.0 2.5 *)\n")
        nome_temp = f.name
    linhas = []
    sucesso = lerArquivo(nome_temp, linhas)
    print(f"  [{'OK' if sucesso and len(linhas) == 3 else 'FALHOU'}] Arquivo valido: {len(linhas)} linhas (esperado: 3)")
    os.unlink(nome_temp)
    print("=" * 60)

def testar_geracao_assembly():
    print("\n" + "=" * 60)
    print("TESTES DE GERACAO DE ASSEMBLY")
    print("=" * 60)
    exprs = [
        "(3.14 2.0 +)",
        "((1.5 2.0 *) (3.0 4.0 *) /)",
        "(5.0 MEM)",
        "(2 RES)",
        "(2.0 3 ^)",
        "(10 3 //)",
        "(10 3 %)",
    ]
    todas = []
    for e in exprs:
        t = []
        parseExpressao(e, t)
        todas.append(t)
    codigo = []
    gerarAssembly(todas, codigo)
    s = '\n'.join(codigo)
    checks = [
        (".section .data",    "Secao .data"),
        (".section .text",    "Secao .text"),
        ("_start:",           "Label _start"),
        ("FPEXC",             "Habilitacao VFP"),
        ("VADD.F64",          "Instrucao VADD.F64"),
        ("VDIV.F64",          "Instrucao VDIV.F64"),
        ("BL potencia_func",  "Chamada a potencia_func"),
        ("BL div_inteira",    "Chamada a div_inteira"),
        ("JTAG_UART_BASE",    "JTAG UART configurado"),
        (".word 0x",          "Constantes .word IEEE 754"),
        ("mem_MEM",           "Variavel de memoria MEM"),
    ]
    for pat, desc in checks:
        print(f"  [{'OK' if pat in s else 'FALHOU'}] {desc}")
    print(f"  [{'OK' if len(codigo) > 50 else 'FALHOU'}] Assembly tem {len(codigo)} linhas")
    print("=" * 60)
