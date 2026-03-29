# INTEGRANTES:
# Anabelly Sthephany Paiva Montibeller | nabelly19
# andressa... | \
# Camila Vieira de Oliveira | camila-vieirao
# Guilherme Ferraz | Guilhermeffda \
#
# NOME DO GRUPO: RA1-16

import sys
import math
import json
from config import TOKEN_NUM, TOKEN_OP, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_RES, TOKEN_IDENT
 
 
# ==============================================================================
# FUNÇÃO: parseExpressao
#
# Analisa uma linha de texto e extrai tokens usando o AFD.
# Cada estado do AFD é uma função definida em utils/parse_expressao.py.
#
# Parâmetros:
#   linha  (str)  - linha de texto com expressão RPN
#   tokens (list) - lista onde os tokens serão adicionados (tuplas (tipo, valor))
#
# Retorna:
#   True se a análise léxica foi bem sucedida, False caso contrário.
# ==============================================================================
 
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
 
 
# ==============================================================================
# FUNÇÃO: executarExpressao
#
# Avalia a expressão RPN representada pelos tokens para fins de VALIDAÇÃO.
# A computação real ocorre no Assembly gerado. Esta função serve para
# comparar os resultados esperados com o que o CPUlator produzirá.
# ==============================================================================
 
def executarExpressao(tokens, resultados, memoria):
    """
    Avalia uma expressão RPN usando uma pilha, para fins de validação.
    Percorre os tokens recursivamente, processando sub-expressões aninhadas.

    Args: 
        tokens (list): Lista de tokens da expressão RPN.
        resultados (list): Lista de resultados anteriores.
        memoria (dict): Dicionário representando a memória.

    Returns:
        float: Resultado da avaliação da expressão, ou None em caso de erro.
    """
    pos_ref = [0]  # Lista com 1 elemento = referência mutável para a posição
 
    def _avaliar(tokens, pos_ref, resultados, memoria):
        if pos_ref[0] >= len(tokens):
            return None
 
        tipo, valor = tokens[pos_ref[0]]
 
        if tipo == TOKEN_NUM:
            pos_ref[0] += 1
            return float(valor)
 
        if tipo == TOKEN_LPAREN:
            pos_ref[0] += 1
 
            # (IDENT) - recall de memória
            if (pos_ref[0] < len(tokens) and
                tokens[pos_ref[0]][0] == TOKEN_IDENT and
                pos_ref[0] + 1 < len(tokens) and
                tokens[pos_ref[0] + 1][0] == TOKEN_RPAREN):
                nome_mem = tokens[pos_ref[0]][1]
                pos_ref[0] += 2
                return memoria.get(nome_mem, 0.0)
 
            # (NUM RES) - resultado anterior
            if (pos_ref[0] < len(tokens) and
                tokens[pos_ref[0]][0] == TOKEN_NUM and
                pos_ref[0] + 1 < len(tokens) and
                tokens[pos_ref[0] + 1][0] == TOKEN_RES):
                n = int(float(tokens[pos_ref[0]][1]))
                pos_ref[0] += 3  # Pula NUM, RES e ')'
                indice = len(resultados) - n
                if 0 <= indice < len(resultados):
                    return resultados[indice]
                else:
                    print(f"  AVISO: RES({n}) fora do alcance, retornando 0.0")
                    return 0.0
 
            # Avalia primeiro operando
            operando_a = _avaliar(tokens, pos_ref, resultados, memoria)
            if operando_a is None:
                return None
 
            if pos_ref[0] < len(tokens):
                prox_tipo, prox_valor = tokens[pos_ref[0]]
 
                # (V IDENT) - store em memória
                if prox_tipo == TOKEN_IDENT:
                    nome_mem = prox_valor
                    pos_ref[0] += 2  # Pula IDENT e ')'
                    memoria[nome_mem] = operando_a
                    return operando_a
 
                # (V RES)
                if prox_tipo == TOKEN_RES:
                    n = int(operando_a)
                    pos_ref[0] += 2
                    indice = len(resultados) - n
                    if 0 <= indice < len(resultados):
                        return resultados[indice]
                    return 0.0
 
            # Avalia segundo operando
            operando_b = _avaliar(tokens, pos_ref, resultados, memoria)
            if operando_b is None:
                return None
 
            if pos_ref[0] >= len(tokens):
                return None
            tipo_op, valor_op = tokens[pos_ref[0]]
            pos_ref[0] += 2  # Pula OP e ')'
 
            if valor_op == '+':
                return operando_a + operando_b
            elif valor_op == '-':
                return operando_a - operando_b
            elif valor_op == '*':
                return operando_a * operando_b
            elif valor_op == '/':
                if operando_b == 0:
                    print("  AVISO: Divisao por zero")
                    return float('inf')
                return operando_a / operando_b
            elif valor_op == '//':
                if operando_b == 0:
                    return 0.0
                return float(int(operando_a) // int(operando_b))
            elif valor_op == '%':
                if operando_b == 0:
                    return 0.0
                return float(int(operando_a) % int(operando_b))
            elif valor_op == '^':
                expoente = int(operando_b)
                resultado = 1.0
                for _ in range(expoente):
                    resultado *= operando_a
                return resultado
            else:
                print(f"  ERRO: Operador desconhecido '{valor_op}'")
                return None
 
        return None
 
    return _avaliar(tokens, pos_ref, resultados, memoria)
 
 
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
 
    ctx = ContextoAssembly()
 
    # Etapa 1: Gera código Assembly para cada linha a partir dos tokens.
    # _gerar_codigo_expressao percorre recursivamente o vetor de tokens.
    codigos_linhas = []
    for idx, tokens in enumerate(todas_linhas_tokens):
        codigo_linha, _ = _gerar_codigo_expressao(tokens, 0, idx, ctx)
        codigos_linhas.append(codigo_linha)
 
    # Etapa 2: Seção .data
    data_section = [
        "@ ======================================================================",
        "@ Codigo Assembly ARMv7 gerado automaticamente pelo compilador RPN",
        "@ Plataforma: CPUlator DE1-SoC (v16.1)",
        "@ Aritmetica: IEEE 754, 64 bits (double precision)",
        "@ ======================================================================",
        "",
        ".global _start",
        "",
        "@ --- Secao de dados ---",
        ".section .data",
        "",
        "@ Constantes double (IEEE 754, codificadas como pares de .word)",
    ]
 
    for valor_str, label in sorted(ctx.constantes.items(), key=lambda x: x[1]):
        val = float(valor_str)
        low, high = double_para_words(val)
        data_section += [
            f"    .align 3",
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
                f"    .align 3",
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
    text_section = [
        "",
        "@ --- Secao de texto ---",
        ".section .text",
        "",
        "_start:",
        "    @ ===== HABILITAR COPROCESSADOR VFP (ESSENCIAL) =====",
        "    MRC p15, 0, R0, c1, c0, 2",
        "    ORR R0, R0, #0x00F00000",
        "    MCR p15, 0, R0, c1, c0, 2",
        "    MOV R0, #0x40000000",
        "    VMSR FPEXC, R0",
        "",
        "    @ Inicializa ponteiros",
        "    LDR R4, =pilha_rpn",
        "    LDR R5, =resultados",
        "",
    ]
 
    for idx, codigo_linha in enumerate(codigos_linhas):
        text_section += [
            f"    @ ========== Linha {idx} ==========",
            f"    LDR R4, =pilha_rpn",
            f"",
        ]
        text_section += codigo_linha
        text_section += [
            f"",
            f"    @ Armazena resultado da linha {idx}",
            f"    SUB R4, R4, #8",
            f"    VLDR.F64 D0, [R4]",
            f"    LDR R0, =resultados",
            f"    ADD R0, R0, #{idx * 8}",
            f"    VSTR.F64 D0, [R0]",
            f"",
            f"    @ LEDs: linha {idx + 1}",
            f"    LDR R0, =LED_BASE",
            f"    MOV R1, #{idx + 1}",
            f"    STR R1, [R0]",
            f"",
            f"    @ HEX: mostra parte inteira do resultado da linha {idx}",
            f"    LDR R0, =resultados",
            f"    ADD R0, R0, #{idx * 8}",
            f"    VLDR.F64 D0, [R0]",
            f"    VABS.F64 D1, D0",
            f"    VCVT.U32.F64 S4, D1",
            f"    VMOV R0, S4",
            f"    BL exibir_hex",
            f"",
            f"    @ UART: imprime 'Linha {idx}: <resultado>'",
            f"    LDR R0, =str_linha",
            f"    BL uart_print_string",
            f"    MOV R0, #{idx}",
            f"    BL uart_print_int",
            f"    LDR R0, =str_doispontos",
            f"    BL uart_print_string",
            f"    LDR R0, =resultados",
            f"    ADD R0, R0, #{idx * 8}",
            f"    VLDR.F64 D0, [R0]",
            f"    BL uart_print_double",
            f"    LDR R0, =str_newline",
            f"    BL uart_print_string",
            f"",
        ]
 
    # Ao final, acende todos os LEDs e imprime FIM
    text_section += [
        f"    @ LEDs: todos acesos = fim",
        f"    LDR R0, =LED_BASE",
        f"    LDR R1, =0x3FF",
        f"    STR R1, [R0]",
        f"",
        f"    LDR R0, =str_fim",
        f"    BL uart_print_string",
        f"",
        f"fim:",
        f"    B fim",
        f"",
    ]
 
    # Etapa 4: Sub-rotinas
    subroutines = [
        "@ ======================================================================",
        "@ SUB-ROTINAS",
        "@ ======================================================================",
        "",
        "uart_print_char:",
        "    PUSH {R1-R2, LR}",
        "    LDR R1, =JTAG_UART_BASE",
        "uart_wait:",
        "    LDR R2, [R1, #4]",
        "    LSR R2, R2, #16",
        "    CMP R2, #0",
        "    BEQ uart_wait",
        "    STR R0, [R1]",
        "    POP {R1-R2, PC}",
        "",
        "uart_print_string:",
        "    PUSH {R0-R1, LR}",
        "    MOV R1, R0",
        "ups_loop:",
        "    LDRB R0, [R1], #1",
        "    CMP R0, #0",
        "    BEQ ups_done",
        "    BL uart_print_char",
        "    B ups_loop",
        "ups_done:",
        "    POP {R0-R1, PC}",
        "",
        "uart_print_int:",
        "    PUSH {R0-R5, LR}",
        "    LDR R1, =print_buffer",
        "    ADD R1, R1, #20",
        "    MOV R2, #0",
        "    STRB R2, [R1]",
        "    MOV R3, R0",
        "    CMP R3, #0",
        "    BNE upi_loop",
        "    SUB R1, R1, #1",
        "    MOV R2, #48",
        "    STRB R2, [R1]",
        "    B upi_print",
        "upi_loop:",
        "    CMP R3, #0",
        "    BEQ upi_print",
        "    MOV R4, #10",
        "    MOV R5, #0",
        "    MOV R0, R3",
        "upi_div:",
        "    CMP R0, R4",
        "    BLT upi_mod_done",
        "    SUB R0, R0, R4",
        "    ADD R5, R5, #1",
        "    B upi_div",
        "upi_mod_done:",
        "    ADD R0, R0, #48",
        "    SUB R1, R1, #1",
        "    STRB R0, [R1]",
        "    MOV R3, R5",
        "    B upi_loop",
        "upi_print:",
        "    MOV R0, R1",
        "    BL uart_print_string",
        "    POP {R0-R5, PC}",
        "",
        "uart_print_double:",
        "    PUSH {R0-R6, LR}",
        "    VPUSH {D0-D5}",
        "    VMOV R0, R1, D0",
        "    TST R1, #0x80000000",
        "    BEQ upd_pos",
        "    LDR R0, =str_menos",
        "    BL uart_print_string",
        "    VNEG.F64 D0, D0",
        "upd_pos:",
        "    VCVT.U32.F64 S10, D0",
        "    VMOV R0, S10",
        "    BL uart_print_int",
        "    LDR R0, =str_ponto",
        "    BL uart_print_string",
        "    VCVT.F64.U32 D1, S10",
        "    VSUB.F64 D2, D0, D1",
        "    LDR R0, =double_milhao",
        "    VLDR.F64 D3, [R0]",
        "    VMUL.F64 D4, D2, D3",
        "    VCVT.U32.F64 S10, D4",
        "    VMOV R3, S10",
        "    MOV R4, #6",
        "    LDR R5, =100000",
        "upd_dec_loop:",
        "    CMP R4, #0",
        "    BEQ upd_done",
        "    MOV R0, R3",
        "    MOV R1, R5",
        "    MOV R2, #0",
        "upd_dec_div:",
        "    CMP R0, R1",
        "    BLT upd_dec_div_done",
        "    SUB R0, R0, R1",
        "    ADD R2, R2, #1",
        "    B upd_dec_div",
        "upd_dec_div_done:",
        "    MOV R3, R0",
        "    ADD R0, R2, #48",
        "    BL uart_print_char",
        "    MOV R0, R5",
        "    MOV R1, #10",
        "    MOV R2, #0",
        "upd_r5div:",
        "    CMP R0, R1",
        "    BLT upd_r5done",
        "    SUB R0, R0, R1",
        "    ADD R2, R2, #1",
        "    B upd_r5div",
        "upd_r5done:",
        "    MOV R5, R2",
        "    SUB R4, R4, #1",
        "    B upd_dec_loop",
        "upd_done:",
        "    VPOP {D0-D5}",
        "    POP {R0-R6, PC}",
        "",
        "div_inteira:",
        "    PUSH {R1-R5, LR}",
        "    MOV R5, #0",
        "    CMP R0, #0",
        "    BGE di_a_pos",
        "    RSB R0, R0, #0",
        "    EOR R5, R5, #1",
        "di_a_pos:",
        "    CMP R1, #0",
        "    BGE di_b_pos",
        "    RSB R1, R1, #0",
        "    EOR R5, R5, #1",
        "di_b_pos:",
        "    MOV R2, #0",
        "di_loop:",
        "    CMP R0, R1",
        "    BLT di_fim",
        "    SUB R0, R0, R1",
        "    ADD R2, R2, #1",
        "    B di_loop",
        "di_fim:",
        "    MOV R0, R2",
        "    CMP R5, #1",
        "    BNE di_ret",
        "    RSB R0, R0, #0",
        "di_ret:",
        "    POP {R1-R5, PC}",
        "",
        "potencia_func:",
        "    PUSH {R1-R2, LR}",
        "    VMOV.F64 D2, D0",
        "    CMP R1, #0",
        "    BNE pf_check1",
        "    LDR R0, =double_um",
        "    VLDR.F64 D2, [R0]",
        "    POP {R1-R2, PC}",
        "pf_check1:",
        "    CMP R1, #1",
        "    BEQ pf_fim",
        "    VMOV.F64 D7, D0",
        "    SUB R1, R1, #1",
        "pf_loop:",
        "    VMUL.F64 D2, D2, D7",
        "    SUBS R1, R1, #1",
        "    BNE pf_loop",
        "pf_fim:",
        "    POP {R1-R2, PC}",
        "",
        "exibir_hex:",
        "    PUSH {R0-R3, R7-R10, LR}",
        "    MOV R7, R0",
        "    MOV R10, #0",
        "    MOV R8, #10",
        "    BL mod_r7_r8",
        "    LDR R1, =tabela_7seg",
        "    LDR R0, [R1, R0, LSL #2]",
        "    ORR R10, R10, R0",
        "    MOV R0, R7",
        "    MOV R1, #10",
        "    BL div_simples",
        "    MOV R7, R0",
        "    MOV R8, #10",
        "    BL mod_r7_r8",
        "    LDR R1, =tabela_7seg",
        "    LDR R0, [R1, R0, LSL #2]",
        "    LSL R0, R0, #8",
        "    ORR R10, R10, R0",
        "    MOV R0, R7",
        "    MOV R1, #10",
        "    BL div_simples",
        "    MOV R7, R0",
        "    MOV R8, #10",
        "    BL mod_r7_r8",
        "    LDR R1, =tabela_7seg",
        "    LDR R0, [R1, R0, LSL #2]",
        "    LSL R0, R0, #16",
        "    ORR R10, R10, R0",
        "    MOV R0, R7",
        "    MOV R1, #10",
        "    BL div_simples",
        "    MOV R7, R0",
        "    MOV R8, #10",
        "    BL mod_r7_r8",
        "    LDR R1, =tabela_7seg",
        "    LDR R0, [R1, R0, LSL #2]",
        "    LSL R0, R0, #24",
        "    ORR R10, R10, R0",
        "    LDR R0, =HEX30_BASE",
        "    STR R10, [R0]",
        "    POP {R0-R3, R7-R10, PC}",
        "",
        "mod_r7_r8:",
        "    PUSH {R1-R2, LR}",
        "    MOV R0, R7",
        "    MOV R1, R8",
        "mr8_loop:",
        "    CMP R0, R1",
        "    BLT mr8_fim",
        "    SUB R0, R0, R1",
        "    B mr8_loop",
        "mr8_fim:",
        "    POP {R1-R2, PC}",
        "",
        "div_simples:",
        "    PUSH {R1-R2, LR}",
        "    MOV R2, #0",
        "ds_loop:",
        "    CMP R0, R1",
        "    BLT ds_fim",
        "    SUB R0, R0, R1",
        "    ADD R2, R2, #1",
        "    B ds_loop",
        "ds_fim:",
        "    MOV R0, R2",
        "    POP {R1-R2, PC}",
        "",
        ".end",
    ]
 
    codigo_assembly.extend(data_section)
    codigo_assembly.extend(text_section)
    codigo_assembly.extend(subroutines)
 
 
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
 
 
# ==============================================================================
# FUNÇÃO: exibirResultados
# ==============================================================================
 
def exibirResultados(resultados):
    """Exibe os resultados de validação calculados em Python.
    
    Args:
        resultados (list): Lista de resultados calculados.
    Returns:
        None: Os resultados são exibidos no console.
    """
    print("\n" + "=" * 60)
    print("RESULTADOS (validacao em Python):")
    print("=" * 60)
    for i, res in enumerate(resultados):
        if res is not None:
            if res == int(res) and not math.isinf(res):
                print(f"  Linha {i}: {int(res)}")
            else:
                print(f"  Linha {i}: {res:.6f}")
        else:
            print(f"  Linha {i}: ERRO")
    print("=" * 60)
 
 
# ==============================================================================
# MAIN
# ==============================================================================
 
def main():
    if len(sys.argv) < 2:
        print("Uso: python ra1.py <arquivo_teste> [--testes]")
        sys.exit(1)
 
    if '--testes' in sys.argv:
        from automated_tests import (
            testar_analisador_lexico, testar_execucao,
            testar_leitura_arquivo, testar_geracao_assembly
        )
        testar_analisador_lexico()
        testar_execucao()
        testar_leitura_arquivo()
        testar_geracao_assembly()
        if len(sys.argv) == 2:
            return
 
    nome_arquivo = sys.argv[1]
    if nome_arquivo == '--testes':
        nome_arquivo = sys.argv[2] if len(sys.argv) > 2 else None
        if not nome_arquivo:
            return
 
    print(f"\n{'=' * 60}")
    print("Compilador RPN -> Assembly ARMv7")
    print(f"Arquivo: {nome_arquivo}")
    print(f"{'=' * 60}")
 
    linhas = []
    if not lerArquivo(nome_arquivo, linhas):
        sys.exit(1)
 
    print(f"\nLinhas lidas: {len(linhas)}")
    for i, l in enumerate(linhas):
        print(f"  [{i}] {l}")
 
    print(f"\n{'=' * 60}")
    print("ANALISE LEXICA")
    print(f"{'=' * 60}")
 
    todas_linhas_tokens = []
    for i, linha in enumerate(linhas):
        tokens = []
        print(f"\n  Linha {i}: {linha}")
        sucesso = parseExpressao(linha, tokens)
        if sucesso:
            print(f"    Tokens: {tokens}")
            todas_linhas_tokens.append(tokens)
        else:
            todas_linhas_tokens.append([])
 
    print(f"\n{'=' * 60}")
    print("EXECUCAO (validacao)")
    print(f"{'=' * 60}")
 
    resultados = []
    memoria = {}
    for i, tokens in enumerate(todas_linhas_tokens):
        if not tokens:
            resultados.append(None)
            continue
        resultado = executarExpressao(tokens, resultados, memoria)
        resultados.append(resultado)
        if resultado is not None:
            print(f"  Linha {i}: {resultado}")
 
    exibirResultados(resultados)
 
    print(f"\n{'=' * 60}")
    print("GERACAO DE ASSEMBLY ARMv7")
    print(f"{'=' * 60}")
 
    codigo_assembly = []
    gerarAssembly(todas_linhas_tokens, codigo_assembly)
 
    nome_base = nome_arquivo.rsplit('.', 1)[0] if '.' in nome_arquivo else nome_arquivo
    nome_assembly = nome_base + ".s"
 
    with open(nome_assembly, 'w', encoding='utf-8') as f:
        for linha in codigo_assembly:
            f.write(linha + '\n')
    print(f"  Assembly: {nome_assembly} ({len(codigo_assembly)} linhas)")
 
    nome_tokens = "tokens.txt"
    with open(nome_tokens, 'w', encoding='utf-8') as f:
        for i, tokens in enumerate(todas_linhas_tokens):
            tokens_fmt = [{"tipo": t[0], "valor": t[1]} for t in tokens]
            f.write(f"Linha {i}: {json.dumps(tokens_fmt, ensure_ascii=False)}\n")
    print(f"  Tokens:   {nome_tokens}")
 
 
if __name__ == "__main__":
    main()
