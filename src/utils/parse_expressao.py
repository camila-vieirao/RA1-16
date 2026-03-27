# ==============================================================================
# Funções de estado do Autômato Finito Determinístico (AFD)
# O AFD reconhece: números reais, operadores, parênteses, RES, identificadores.
#
# Estados:
#   estado_inicial        -> q0: classifica o primeiro caractere
#   estado_numero         -> q1: acumula dígitos da parte inteira
#   estado_numero_decimal -> q2: acumula dígitos da parte decimal
#   estado_barra          -> q3: diferencia '/' de '//'
#   estado_identificador  -> q4: acumula letras (inicia com maiúscula)
#
# Cada função recebe (char, contexto) e retorna a próxima função de estado,
# ou None em caso de erro léxico.
#
# O contexto inclui um contador 'nivel_parenteses' para detectar desbalanceamento
# ==============================================================================

from config import TOKEN_NUM, TOKEN_OP, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_RES, TOKEN_IDENT


def estado_inicial(char, contexto):
    """
    Estado inicial do AFD (q0).
    Classifica o caractere e decide a transição.
    
    Ao encontrar '(' ou ')', atualiza o contador de nível de parênteses
    para possibilitar a detecção de desbalanceamento.
    """
    if char == ' ' or char == '\t' or char == '\n' or char == '\r':
        return estado_inicial

    elif char.isdigit():
        contexto['token_atual'] = char
        return estado_numero

    elif char == '(':
        contexto['nivel_parenteses'] += 1
        contexto['tokens'].append((TOKEN_LPAREN, '('))
        return estado_inicial

    elif char == ')':
        contexto['nivel_parenteses'] -= 1
        if contexto['nivel_parenteses'] < 0:
            contexto['erro'] = (
                f"Parentese de fechamento sem abertura correspondente "
                f"na posicao {contexto['posicao']}"
            )
            return None
        contexto['tokens'].append((TOKEN_RPAREN, ')'))
        return estado_inicial

    elif char in ('+', '-', '*', '%', '^'):
        contexto['tokens'].append((TOKEN_OP, char))
        return estado_inicial

    elif char == '/':
        contexto['token_atual'] = '/'
        return estado_barra

    elif char.isupper():
        # Identificadores iniciam com letra maiúscula (A-Z)
        contexto['token_atual'] = char
        return estado_identificador

    else:
        contexto['erro'] = (
            f"Caractere invalido '{char}' na posicao {contexto['posicao']}"
        )
        return None


def estado_numero(char, contexto):
    """
    Estado de leitura da parte inteira de um número (q1).
    Acumula dígitos. Se encontrar '.', transita para q2 (parte decimal).
    """
    if char.isdigit():
        contexto['token_atual'] += char
        return estado_numero

    elif char == '.':
        if '.' in contexto['token_atual']:
            contexto['erro'] = (
                f"Numero malformado '{contexto['token_atual']}.' "
                f"na posicao {contexto['posicao']} (multiplos pontos decimais)"
            )
            return None
        contexto['token_atual'] += '.'
        return estado_numero_decimal

    elif char == ' ' or char == '\t' or char == '\n' or char == '\r':
        contexto['tokens'].append((TOKEN_NUM, contexto['token_atual']))
        contexto['token_atual'] = ''
        return estado_inicial

    elif char == ')':
        contexto['tokens'].append((TOKEN_NUM, contexto['token_atual']))
        contexto['token_atual'] = ''
        contexto['nivel_parenteses'] -= 1
        if contexto['nivel_parenteses'] < 0:
            contexto['erro'] = (
                f"Parentese de fechamento sem abertura correspondente "
                f"na posicao {contexto['posicao']}"
            )
            return None
        contexto['tokens'].append((TOKEN_RPAREN, ')'))
        return estado_inicial

    elif char == '(':
        contexto['tokens'].append((TOKEN_NUM, contexto['token_atual']))
        contexto['token_atual'] = ''
        contexto['nivel_parenteses'] += 1
        contexto['tokens'].append((TOKEN_LPAREN, '('))
        return estado_inicial

    else:
        contexto['erro'] = (
            f"Caractere inesperado '{char}' apos numero "
            f"'{contexto['token_atual']}' na posicao {contexto['posicao']}"
        )
        return None


def estado_numero_decimal(char, contexto):
    """
    Estado de leitura da parte decimal de um número (q2).
    Se encontrar outro '.', é erro (ex: 3.14.5).
    """
    if char.isdigit():
        contexto['token_atual'] += char
        return estado_numero_decimal

    elif char == '.':
        contexto['erro'] = (
            f"Numero malformado '{contexto['token_atual']}.' "
            f"na posicao {contexto['posicao']} (multiplos pontos decimais)"
        )
        return None

    elif char == ' ' or char == '\t' or char == '\n' or char == '\r':
        contexto['tokens'].append((TOKEN_NUM, contexto['token_atual']))
        contexto['token_atual'] = ''
        return estado_inicial

    elif char == ')':
        contexto['tokens'].append((TOKEN_NUM, contexto['token_atual']))
        contexto['token_atual'] = ''
        contexto['nivel_parenteses'] -= 1
        if contexto['nivel_parenteses'] < 0:
            contexto['erro'] = (
                f"Parentese de fechamento sem abertura correspondente "
                f"na posicao {contexto['posicao']}"
            )
            return None
        contexto['tokens'].append((TOKEN_RPAREN, ')'))
        return estado_inicial

    elif char == '(':
        contexto['tokens'].append((TOKEN_NUM, contexto['token_atual']))
        contexto['token_atual'] = ''
        contexto['nivel_parenteses'] += 1
        contexto['tokens'].append((TOKEN_LPAREN, '('))
        return estado_inicial

    else:
        contexto['erro'] = (
            f"Caractere inesperado '{char}' apos numero "
            f"'{contexto['token_atual']}' na posicao {contexto['posicao']}"
        )
        return None


def estado_barra(char, contexto):
    """
    Estado após ler '/' (q3).
    Se próximo é '/', emite '//'. Senão emite '/' e marca reprocessar.
    """
    if char == '/':
        contexto['tokens'].append((TOKEN_OP, '//'))
        contexto['token_atual'] = ''
        return estado_inicial
    else:
        contexto['tokens'].append((TOKEN_OP, '/'))
        contexto['token_atual'] = ''
        contexto['reprocessar'] = True
        return estado_inicial


def estado_identificador(char, contexto):
    """
    Estado de leitura de identificador (q4).
    Acumula letras maiúsculas [A-Z].
    Ao finalizar, verifica se é a keyword RES ou um nome de memória.

    Transições:
      - letra maiúscula [A-Z] -> estado_identificador (continua)
      - espaço/)              -> emite RES ou IDENT, processa caractere
      - letra minúscula       -> ERRO (identificador deve ser todo maiúsculo)
      - outro                 -> ERRO
    """
    if char.isupper():
        # Continua acumulando letras do identificador
        contexto['token_atual'] += char
        return estado_identificador

    elif char.islower():
        # Letra minúscula em identificador: ERRO
        contexto['erro'] = (
            f"Identificador invalido '{contexto['token_atual']}{char}' "
            f"na posicao {contexto['posicao']} "
            f"(identificadores devem conter apenas letras maiusculas)"
        )
        return None

    elif char == ' ' or char == '\t' or char == '\n' or char == '\r':
        # Fim do identificador: classifica como RES ou IDENT
        ident = contexto['token_atual']
        if ident == 'RES':
            contexto['tokens'].append((TOKEN_RES, 'RES'))
        else:
            contexto['tokens'].append((TOKEN_IDENT, ident))
        contexto['token_atual'] = ''
        return estado_inicial

    elif char == ')':
        # Fim do identificador seguido de parêntese
        ident = contexto['token_atual']
        if ident == 'RES':
            contexto['tokens'].append((TOKEN_RES, 'RES'))
        else:
            contexto['tokens'].append((TOKEN_IDENT, ident))
        contexto['token_atual'] = ''
        contexto['nivel_parenteses'] -= 1
        contexto['tokens'].append((TOKEN_RPAREN, ')'))
        return estado_inicial

    elif char == '(':
        ident = contexto['token_atual']
        if ident == 'RES':
            contexto['tokens'].append((TOKEN_RES, 'RES'))
        else:
            contexto['tokens'].append((TOKEN_IDENT, ident))
        contexto['token_atual'] = ''
        contexto['tokens'].append((TOKEN_LPAREN, '('))
        return estado_inicial

    else:
        contexto['erro'] = (
            f"Caractere inesperado '{char}' em identificador "
            f"'{contexto['token_atual']}' na posicao {contexto['posicao']}"
        )
        return None
