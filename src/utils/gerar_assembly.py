# ==============================================================================
# Contém as classes e funções auxiliares para geração de código Assembly ARMv7:
#   - double_para_words: converte float Python para par de .word IEEE 754
#   - ContextoAssembly: mantém estado (constantes, variáveis, labels)
#   - _gerar_codigo_expressao: gera Assembly recursivamente a partir dos tokens
# ==============================================================================

import struct
from config import TOKEN_NUM, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_RES, TOKEN_IDENT


def double_para_words(valor):
    """
    Converte um float Python para par de words de 32 bits (IEEE 754 double).
    Retorna (low_word, high_word) em formato little-endian (ARM).
    
    Exemplo: 3.14 -> (0x51EB851F, 0x40091EB8)
    
    O ARM é little-endian: o byte menos significativo fica no endereço
    mais baixo. Por isso o .word baixo (bits 0-31) vem primeiro na memória,
    e o .word alto (bits 32-63) vem depois.

    Args:
        valor (float): O número a ser convertido.
    Returns:
        (int, int): Tupla (low_word, high_word) representando o double em IEEE 754.
    """
    bytes_val = struct.pack('<d', float(valor))
    low = struct.unpack('<I', bytes_val[0:4])[0]
    high = struct.unpack('<I', bytes_val[4:8])[0]
    return low, high


class ContextoAssembly:
    """
    Contexto auxiliar para geração de código Assembly ARMv7.
    
    Mantém registro de:
      - constantes: dicionário valor_str -> label (ex: "3.14" -> "const_0")
      - variaveis_mem: conjunto de nomes de variáveis MEM usadas
      - cont_labels: contador para gerar labels únicos
    """

    def __init__(self):
        self.constantes = {}
        self.cont_constantes = 0
        self.variaveis_mem = set()
        self.cont_labels = 0

    def adicionar_constante(self, valor_str):
        """Registra uma constante double e retorna seu label. Evita duplicatas."""
        if valor_str not in self.constantes:
            label = f"const_{self.cont_constantes}"
            self.constantes[valor_str] = label
            self.cont_constantes += 1
        return self.constantes[valor_str]

    def adicionar_variavel_mem(self, nome):
        """Registra uma variável de memória."""
        self.variaveis_mem.add(nome)

    def novo_label(self, prefixo="L"):
        """Gera um label único para uso em desvios."""
        label = f"{prefixo}_{self.cont_labels}"
        self.cont_labels += 1
        return label


def _gerar_codigo_expressao(tokens, pos, indice_linha, ctx):
    """
    Gera código Assembly ARMv7 para uma expressão RPN.
    
    Esta função percorre recursivamente a lista de tokens (que veio do
    analisador léxico) e, para cada padrão reconhecido, emite as instruções
    Assembly correspondentes. NÃO relê o arquivo de entrada — trabalha
    exclusivamente sobre o vetor de tokens já produzido pelo parseExpressao.
    
    Convenção de pilha RPN em Assembly:
      - R4 aponta para o próximo espaço livre no topo da pilha
      - Push: VSTR D0, [R4] + ADD R4, #8
      - Pop:  SUB R4, #8 + VLDR D0, [R4]
    
    Padrões reconhecidos:
      1. NUM           -> empilha constante
      2. (IDENT)       -> empilha valor da variável de memória
      3. (NUM RES)     -> empilha resultado de N linhas atrás
      4. (V IDENT)     -> avalia V, armazena na variável, empilha V
      5. (A B OP)      -> avalia A, avalia B, aplica operação, empilha resultado
    
    Args:
      tokens       - lista de tokens (tuplas) da linha atual
      pos          - posição atual na lista de tokens
      indice_linha - índice da linha (usado para calcular offsets de RES)
      ctx          - ContextoAssembly com constantes e variáveis registradas
    
    Returns:
      (lista_de_linhas_assembly, nova_posição_nos_tokens)
    """
    if pos >= len(tokens):
        return [], pos

    tipo, valor = tokens[pos]

    # ---- Caso 1: Token é um número literal ----
    # Registra a constante no ContextoAssembly, gera código para carregá-la
    # da seção .data para o registrador VFP D0, e empilha na pilha RPN.
    if tipo == TOKEN_NUM:
        label = ctx.adicionar_constante(valor)
        codigo = [
            f"    @ Push numero {valor}",
            f"    LDR R0, ={label}",
            f"    VLDR.F64 D0, [R0]",
            f"    VSTR.F64 D0, [R4]",
            f"    ADD R4, R4, #8",
        ]
        return codigo, pos + 1

    # ---- Caso 2: Token é parêntese de abertura ----
    # Indica início de uma sub-expressão. Examina os tokens seguintes
    # para determinar qual dos 4 padrões é: (IDENT), (N RES), (V IDENT), (A B OP)
    if tipo == TOKEN_LPAREN:
        pos += 1  # Avança além do '('

        # --- Sub-caso 2a: (IDENT) - Recall de memória ---
        # Padrão: LPAREN seguido de IDENT seguido de RPAREN
        # Gera código que lê o double armazenado em mem_NOME e empilha
        if (pos < len(tokens) and
            tokens[pos][0] == TOKEN_IDENT and
            pos + 1 < len(tokens) and
            tokens[pos + 1][0] == TOKEN_RPAREN):
            nome_mem = tokens[pos][1]
            ctx.adicionar_variavel_mem(nome_mem)
            codigo = [
                f"    @ Recall memoria {nome_mem}",
                f"    LDR R0, =mem_{nome_mem}",
                f"    VLDR.F64 D0, [R0]",
                f"    VSTR.F64 D0, [R4]",
                f"    ADD R4, R4, #8",
            ]
            return codigo, pos + 2  # Pula IDENT e ')'

        # --- Sub-caso 2b: (NUM RES) - Resultado anterior ---
        # Padrão: LPAREN seguido de NUM seguido de RES seguido de RPAREN
        # O offset no vetor resultados é calculado AQUI no Python:
        #   indice_alvo = indice_linha_atual - N
        #   offset = indice_alvo * 8  (cada double tem 8 bytes)
        # O Assembly gerado usa esse offset como literal na instrução ADD.
        if (pos < len(tokens) and
            tokens[pos][0] == TOKEN_NUM and
            pos + 1 < len(tokens) and
            tokens[pos + 1][0] == TOKEN_RES):
            n = int(float(tokens[pos][1]))
            indice_alvo = indice_linha - n
            offset = indice_alvo * 8
            codigo = [
                f"    @ RES {n} (resultado da linha {indice_alvo})",
                f"    LDR R0, =resultados",
                f"    ADD R0, R0, #{offset}",
                f"    VLDR.F64 D0, [R0]",
                f"    VSTR.F64 D0, [R4]",
                f"    ADD R4, R4, #8",
            ]
            pos += 2  # Pula NUM e RES
            pos += 1  # Pula ')'
            return codigo, pos

        # --- Avalia o primeiro operando (recursivamente) ---
        # Pode ser um NUM ou outra sub-expressão (LPAREN...)
        codigo_a, pos = _gerar_codigo_expressao(tokens, pos, indice_linha, ctx)

        if pos >= len(tokens):
            return codigo_a, pos

        # --- Sub-caso 2c: (V IDENT) - Armazenamento em memória ---
        # Após avaliar o primeiro operando, se o próximo token é IDENT,
        # então é um store: grava o valor do topo da pilha em mem_NOME
        if tokens[pos][0] == TOKEN_IDENT:
            nome_mem = tokens[pos][1]
            ctx.adicionar_variavel_mem(nome_mem)
            codigo = codigo_a + [
                f"    @ Store em memoria {nome_mem}",
                f"    SUB R4, R4, #8",
                f"    VLDR.F64 D0, [R4]",
                f"    LDR R0, =mem_{nome_mem}",
                f"    VSTR.F64 D0, [R0]",
                f"    @ Push o valor de volta",
                f"    VSTR.F64 D0, [R4]",
                f"    ADD R4, R4, #8",
            ]
            pos += 1  # Pula IDENT
            pos += 1  # Pula ')'
            return codigo, pos

        # --- Sub-caso 2d: (V RES) onde V é sub-expressão ---
        if tokens[pos][0] == TOKEN_RES:
            pos += 1  # Pula RES
            pos += 1  # Pula ')'
            return codigo_a, pos

        # --- Sub-caso 2e: (A B OP) - Operação aritmética ---
        # Avalia o segundo operando (recursivamente)
        codigo_b, pos = _gerar_codigo_expressao(tokens, pos, indice_linha, ctx)

        if pos >= len(tokens):
            return codigo_a + codigo_b, pos

        tipo_op, valor_op = tokens[pos]
        pos += 1  # Pula OP
        pos += 1  # Pula ')'

        # Gera código Assembly para a operação:
        # 1. Desempilha B em D1 (segundo operando)
        # 2. Desempilha A em D0 (primeiro operando)
        # 3. Executa a operação VFP, resultado em D2
        # 4. Empilha D2
        codigo_op = [
            f"    @ Operacao: {valor_op}",
            f"    SUB R4, R4, #8",
            f"    VLDR.F64 D1, [R4]",
            f"    SUB R4, R4, #8",
            f"    VLDR.F64 D0, [R4]",
        ]

        if valor_op == '+':
            codigo_op += [f"    VADD.F64 D2, D0, D1"]
        elif valor_op == '-':
            codigo_op += [f"    VSUB.F64 D2, D0, D1"]
        elif valor_op == '*':
            codigo_op += [f"    VMUL.F64 D2, D0, D1"]
        elif valor_op == '/':
            codigo_op += [f"    VDIV.F64 D2, D0, D1"]
        elif valor_op == '//':
            codigo_op += [
                f"    @ Divisao inteira",
                f"    VCVT.S32.F64 S0, D0",
                f"    VCVT.S32.F64 S2, D1",
                f"    VMOV R0, S0",
                f"    VMOV R1, S2",
                f"    PUSH {{R4}}",
                f"    BL div_inteira",
                f"    POP {{R4}}",
                f"    VMOV S4, R0",
                f"    VCVT.F64.S32 D2, S4",
            ]
        elif valor_op == '%':
            codigo_op += [
                f"    @ Resto da divisao inteira",
                f"    VCVT.S32.F64 S0, D0",
                f"    VCVT.S32.F64 S2, D1",
                f"    VMOV R0, S0",
                f"    VMOV R1, S2",
                f"    PUSH {{R4}}",
                f"    MOV R3, R0",
                f"    BL div_inteira",
                f"    MUL R2, R0, R1",
                f"    SUB R0, R3, R2",
                f"    POP {{R4}}",
                f"    VMOV S4, R0",
                f"    VCVT.F64.S32 D2, S4",
            ]
        elif valor_op == '^':
            codigo_op += [
                f"    @ Potenciacao",
                f"    VCVT.S32.F64 S2, D1",
                f"    VMOV R1, S2",
                f"    PUSH {{R4}}",
                f"    BL potencia_func",
                f"    POP {{R4}}",
            ]

        codigo_op += [
            f"    VSTR.F64 D2, [R4]",
            f"    ADD R4, R4, #8",
        ]

        return codigo_a + codigo_b + codigo_op, pos

    # Token inesperado — não deveria chegar aqui com tokens válidos
    return [], pos + 1
