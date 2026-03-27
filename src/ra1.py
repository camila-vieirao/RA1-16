# INTEGRANTES:
# Anabelly Sthephany Paiva Montibeller | nabelly19
# andressa... | \
# Camila Vieira de Oliveira | camila-vieirao
# Guilherme Ferraz | Guilhermeffda \
#
# NOME DO GRUPO: RA1-16

import sys
from config import TOKEN_NUM, TOKEN_OP, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_RES, TOKEN_IDENT

# ==============================================================================
# FUNÇÃO: lerArquivo
# ==============================================================================
 
def lerArquivo(nome_arquivo, linhas):
    """Lê o arquivo de entrada. Ignora linhas vazias.
    
    Args:
        nome_arquivo (str): Caminho do arquivo a ser lido.
        linhas (list): Lista para armazenar as linhas lidas (passada por referência).
    Returns:
        bool: True se a leitura foi bem-sucedida, False caso contrário.
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


def parseExpressao(linha, tokens):
    """
    Função principal do analisador léxico.
    Percorre a linha caractere a caractere, delegando a classificação
    para a função do estado corrente do AFD.
    
    Args:
        linha (str): Linha de texto com expressão RPN.
        tokens (list): Lista onde os tokens serão adicionados (tuplas (tipo, valor)).

    Returns:
        bool: True se a análise léxica foi bem sucedida, False caso contrário.
    """
    from utils.parse_expressao import (
        estado_inicial, estado_numero, estado_numero_decimal,
        estado_barra, estado_identificador
    )
 
    # Contexto compartilhado entre todos os estados do AFD
    contexto = {
        'tokens': tokens,         # Lista de tokens (saída)
        'token_atual': '',        # Acumulador do token em construção
        'erro': None,             # Mensagem de erro (se houver)
        'posicao': 0,             # Posição do caractere na linha
        'reprocessar': False,     # Flag: relê o caractere atual no novo estado
        'nivel_parenteses': 0     # Contador para detectar parênteses desbalanceados
    }
 
    # 'estado_corrente' é uma VARIÁVEL que guarda a referência para a função
    # do estado ativo. Começa apontando para estado_inicial (q0).
    # Em Python, funções são objetos — podemos guardá-las em variáveis.
    estado_corrente = estado_inicial
 
    i = 0
    while i < len(linha):
        char = linha[i]
        contexto['posicao'] = i
        contexto['reprocessar'] = False
 
        # Chama a função do estado ativo, passando o caractere atual.
        # A função retorna a PRÓXIMA função de estado (pode ser ela mesma).
        proximo_estado = estado_corrente(char, contexto)
 
        # Se retornou None, houve erro léxico
        if proximo_estado is None:
            if contexto['erro']:
                print(f"  ERRO LEXICO: {contexto['erro']}")
            return False
 
        # Atualiza a variável para apontar para o novo estado
        estado_corrente = proximo_estado
 
        # Se reprocessar=True, NÃO avança i — o mesmo caractere será
        # processado novamente, mas agora pelo novo estado
        if contexto['reprocessar']:
            contexto['reprocessar'] = False
            continue
 
        i += 1
 
    # Fim da linha: se havia um token sendo acumulado, emite-o
    if contexto['token_atual'] != '':
        if estado_corrente == estado_numero or estado_corrente == estado_numero_decimal:
            tokens.append((TOKEN_NUM, contexto['token_atual']))
        elif estado_corrente == estado_identificador:
            ident = contexto['token_atual']
            if ident == 'RES':
                tokens.append((TOKEN_RES, 'RES'))
            else:
                tokens.append((TOKEN_IDENT, ident))
        elif estado_corrente == estado_barra:
            tokens.append((TOKEN_OP, '/'))
        contexto['token_atual'] = ''
 
    # Verificação pós-AFD: parênteses desbalanceados.
    # O contador nivel_parenteses é atualizado pelos estados do AFD:
    #   - Cada '(' incrementa o contador
    #   - Cada ')' decrementa (e se ficar < 0, o estado já retorna erro inline)
    # Aqui verificamos se sobraram parênteses abertos sem fechamento.
    if contexto['nivel_parenteses'] != 0:
        print(f"  ERRO LEXICO: Parenteses desbalanceados "
              f"({contexto['nivel_parenteses']} parentese(s) aberto(s) sem fechamento)")
        return False
 
    return True

def executarExpressao():
    pass

# ==============================================================================
# FUNÇÃO: gerarAssembly
#
# Gera o código Assembly ARMv7 completo para todas as linhas do programa.
# Recebe o vetor de tokens (saída do analisador léxico) — NÃO relê o arquivo.
#
# O fluxo completo é:
#   1. Percorre cada lista de tokens (uma por linha) chamando
#      _gerar_codigo_expressao, que gera Assembly recursivamente.
#      Nessa etapa, o ContextoAssembly registra quais constantes e
#      variáveis de memória são necessárias.
#   2. Monta a seção .data com: constantes (pares .word IEEE 754),
#      variáveis MEM, pilha RPN, vetor de resultados, strings UART.
#   3. Monta a seção .text com: habilitação VFP, código de cada linha
#      (expressão + salvar resultado + LEDs + UART), exibição final HEX.
#   4. Adiciona as sub-rotinas (UART, divisão, potência, HEX).
# ==============================================================================
 
def gerarAssembly(todas_linhas_tokens, codigo_assembly):
    """
    Gera o código Assembly ARMv7 completo para todas as linhas do programa.
    
    Args:
        todas_linhas_tokens (list): Lista de listas de tokens, uma por linha.
        codigo_assembly (list): Lista para armazenar o código Assembly gerado.
    
    Returns:
        None: O código é adicionado à lista 'codigo_assembly' passada por referência.

    """
    from utils.gerar_assembly import ContextoAssembly, _gerar_codigo_expressao, double_para_words
    from utils.constantes_assembly import SUBROUTINES_CONFIG, TEXT_SECTION_CONFIG, DATA_SECTION_CONFIG

    ctx = ContextoAssembly()
 
    # Etapa 1: Gera código Assembly para cada linha a partir dos tokens.
    # _gerar_codigo_expressao percorre recursivamente o vetor de tokens.
    codigos_linhas = []
    for idx, tokens in enumerate(todas_linhas_tokens):
        codigo_linha, _ = _gerar_codigo_expressao(tokens, 0, idx, ctx)
        codigos_linhas.append(codigo_linha)
 
    # Etapa 2: Seção .data
    data_section = DATA_SECTION_CONFIG
 
    for valor_str, label in sorted(ctx.constantes.items(), key=lambda x: x[1]):
        val = float(valor_str)
        low, high = double_para_words(val)
        data_section += [
            "    .align 3",
            f"{label}:  @ double {valor_str}",
            f"    .word 0x{low:08X}",
            f"    .word 0x{high:08X}",
        ]
 
    zero_low, zero_high = double_para_words(0.0)
    um_low, um_high = double_para_words(1.0)
    milhao_low, milhao_high = double_para_words(1000000.0)
 
    data_section += [
        "",
        "@ Constantes auxiliares",
        "    .align 3",
        "double_zero:",
        f"    .word 0x{zero_low:08X}",
        f"    .word 0x{zero_high:08X}",
        "    .align 3",
        "double_um:",
        f"    .word 0x{um_low:08X}",
        f"    .word 0x{um_high:08X}",
        "    .align 3",
        "double_milhao:",
        f"    .word 0x{milhao_low:08X}",
        f"    .word 0x{milhao_high:08X}",
    ]
 
    if ctx.variaveis_mem:
        data_section += ["", "@ Variaveis de memoria"]
        for nome in sorted(ctx.variaveis_mem):
            data_section += [
                "    .align 3",
                f"mem_{nome}:",
                f"    .word 0x{zero_low:08X}",
                f"    .word 0x{zero_high:08X}",
            ]
 
    num_linhas = len(todas_linhas_tokens)
    tamanho_resultados = max(num_linhas * 8, 64)
    data_section += [
        "",
        "    .align 3",
        "pilha_rpn:",
        "    .space 1024",
        "",
        "    .align 3",
        "resultados:",
        f"    .space {tamanho_resultados}",
        "",
        "    .align 2",
        "print_buffer:",
        "    .space 32",
        "",
        "str_linha:",
        '    .asciz "Linha "',
        "    .align 2",
        "str_doispontos:",
        '    .asciz ": "',
        "    .align 2",
        "str_newline:",
        '    .asciz "\\n"',
        "    .align 2",
        "str_menos:",
        '    .asciz "-"',
        "    .align 2",
        "str_ponto:",
        '    .asciz "."',
        "    .align 2",
        "str_espaco:",
        '    .asciz " "',
        "    .align 2",
        "str_fim:",
        '    .asciz "\\n=== FIM ===\\n"',
        "    .align 2",
        "",
        "tabela_7seg:",
        "    .word 0x3F, 0x06, 0x5B, 0x4F, 0x66",
        "    .word 0x6D, 0x7D, 0x07, 0x7F, 0x6F",
        "",
        ".equ LED_BASE,       0xFF200000",
        ".equ HEX30_BASE,     0xFF200020",
        ".equ HEX54_BASE,     0xFF200030",
        ".equ SW_BASE,        0xFF200040",
        ".equ BTN_BASE,       0xFF200050",
        ".equ JTAG_UART_BASE, 0xFF201000",
    ]
 
    # Etapa 3: Seção .text
    text_section = TEXT_SECTION_CONFIG
 
    for idx, codigo_linha in enumerate(codigos_linhas):
        text_section += [
            f"    @ ========== Linha {idx} ==========",
            "    LDR R4, =pilha_rpn",
            "",
        ]
        text_section += codigo_linha
        text_section += [
            "",
            f"    @ Armazena resultado da linha {idx}",
            "    SUB R4, R4, #8",
            "    VLDR.F64 D0, [R4]",
            "    LDR R0, =resultados",
            f"    ADD R0, R0, #{idx * 8}",
            "    VSTR.F64 D0, [R0]",
            "",
            f"    @ LEDs: linha {idx + 1}",
            "    LDR R0, =LED_BASE",
            f"    MOV R1, #{idx + 1}",
            "    STR R1, [R0]",
            "",
            f"    @ HEX: mostra parte inteira do resultado da linha {idx}",
            "    LDR R0, =resultados",
            f"    ADD R0, R0, #{idx * 8}",
            "    VLDR.F64 D0, [R0]",
            "    VABS.F64 D1, D0",
            "    VCVT.U32.F64 S4, D1",
            "    VMOV R0, S4",
            "    BL exibir_hex",
            "",
            f"    @ UART: imprime 'Linha {idx}: <resultado>'",
            "    LDR R0, =str_linha",
            "    BL uart_print_string",
            f"    MOV R0, #{idx}",
            "    BL uart_print_int",
            "    LDR R0, =str_doispontos",
            "    BL uart_print_string",
            "    LDR R0, =resultados",
            f"    ADD R0, R0, #{idx * 8}",
            "    VLDR.F64 D0, [R0]",
            "    BL uart_print_double",
            "    LDR R0, =str_newline",
            "    BL uart_print_string",
            "",
        ]
 
    # Ao final, acende todos os LEDs e imprime FIM
    text_section += [
        "    @ LEDs: todos acesos = fim",
        "    LDR R0, =LED_BASE",
        "    LDR R1, =0x3FF",
        "    STR R1, [R0]",
        "",
        "    LDR R0, =str_fim",
        "    BL uart_print_string",
        "",
        "fim:",
        "    B fim",
        "",
    ]
 
    subroutines = SUBROUTINES_CONFIG
 
    codigo_assembly.extend(data_section)
    codigo_assembly.extend(text_section)
    codigo_assembly.extend(subroutines)


def exibirResultados():
    pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo_entrada>")
        sys.exit(1)

    nome_arquivo = sys.argv[1]
    linhas = []
    if not lerArquivo(nome_arquivo, linhas):
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print("GERACAO DE ASSEMBLY ARMv7")
    print(f"{'=' * 60}")
    codigo_assembly = []

    todas_linhas_tokens = []
    for idx, linha in enumerate(linhas):
        tokens = []
        print(f"\nLinha {idx + 1}: {linha}")
        if not parseExpressao(linha, tokens):
            sys.exit(1)
        todas_linhas_tokens.append(tokens)

    gerarAssembly(todas_linhas_tokens, codigo_assembly)

    nome_base = nome_arquivo.rsplit('.', 1)[0] if '.' in nome_arquivo else nome_arquivo
    nome_assembly = nome_base + ".s"

    with open(nome_assembly, 'w', encoding='utf-8') as f:
        for linha in codigo_assembly:
            f.write(linha + '\n')
    print(f"  Assembly: {nome_assembly} ({len(codigo_assembly)} linhas)")


#     executarExpressao()
#     exibirResultados()
#
