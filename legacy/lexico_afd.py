class ErroLexico(ValueError):
    pass


def _eh_espaco(caractere: str) -> bool:
    return caractere in {" ", "\t", "\n", "\r"}


def _eh_delimitador(linha: str, indice: int) -> bool:
    if indice >= len(linha):
        return True
    return _eh_espaco(linha[indice]) or linha[indice] in {"(", ")"}


def _proximo_inicia_numero(linha: str, indice: int) -> bool:
    proximo = indice + 1
    if proximo >= len(linha):
        return False
    return linha[proximo].isdigit() or linha[proximo] == "."


def _validar_fim_token(linha: str, indice: int, token: str) -> None:
    if not _eh_delimitador(linha, indice):
        raise ErroLexico(f"Token inválido próximo de '{token}'")


def _estado_numero_inicio(linha: str, indice: int):
    token = []

    if linha[indice] in "+-":
        token.append(linha[indice])
        indice += 1
        if indice >= len(linha):
            raise ErroLexico("Número malformado")

    if linha[indice].isdigit():
        return _estado_numero_inteiro(linha, indice, token)

    if linha[indice] == ".":
        token.append(linha[indice])
        indice += 1
        return _estado_numero_fracionario(linha, indice, token)

    raise ErroLexico("Número malformado")


def _estado_numero_inteiro(linha: str, indice: int, token: list):
    while indice < len(linha) and linha[indice].isdigit():
        token.append(linha[indice])
        indice += 1

    if indice < len(linha) and linha[indice] == ".":
        token.append(linha[indice])
        indice += 1
        return _estado_numero_fracionario(linha, indice, token)

    lexema = "".join(token)
    _validar_fim_token(linha, indice, lexema)
    return lexema, indice


def _estado_numero_fracionario(linha: str, indice: int, token: list):
    quantidade_digitos = 0

    while indice < len(linha) and linha[indice].isdigit():
        token.append(linha[indice])
        indice += 1
        quantidade_digitos += 1

    if quantidade_digitos == 0:
        raise ErroLexico("Número malformado")

    lexema = "".join(token)
    _validar_fim_token(linha, indice, lexema)
    return lexema, indice


def _estado_identificador(linha: str, indice: int):
    token = []

    while indice < len(linha) and linha[indice].isalpha():
        if not linha[indice].isupper():
            raise ErroLexico("Identificadores devem conter apenas letras maiúsculas")
        token.append(linha[indice])
        indice += 1

    if not token:
        raise ErroLexico("Identificador inválido")

    lexema = "".join(token)
    _validar_fim_token(linha, indice, lexema)
    return lexema, indice


def _estado_operador_barra(linha: str, indice: int):
    if indice + 1 < len(linha) and linha[indice + 1] == "/":
        token = "//"
        indice += 2
    else:
        token = "/"
        indice += 1

    _validar_fim_token(linha, indice, token)
    return token, indice


def _estado_operador_simples(linha: str, indice: int):
    token = linha[indice]
    indice += 1
    _validar_fim_token(linha, indice, token)
    return token, indice


def _estado_inicial(linha: str, indice: int):
    while indice < len(linha) and _eh_espaco(linha[indice]):
        indice += 1

    if indice >= len(linha):
        return None, indice

    caractere = linha[indice]

    if caractere in {"(", ")"}:
        return caractere, indice + 1

    if caractere == "/":
        return _estado_operador_barra(linha, indice)

    if caractere in "+-":
        if _proximo_inicia_numero(linha, indice):
            return _estado_numero_inicio(linha, indice)
        return _estado_operador_simples(linha, indice)

    if caractere in {"*", "%", "^"}:
        return _estado_operador_simples(linha, indice)

    if caractere.isdigit() or caractere == ".":
        return _estado_numero_inicio(linha, indice)

    if caractere.isalpha():
        return _estado_identificador(linha, indice)

    raise ErroLexico(f"Caractere inválido: '{caractere}'")


def parseExpressao(linha: str, tokens: list = None) -> list:
    """
    Faz a análise léxica de uma linha e retorna o vetor de tokens.

    A implementação usa um AFD com estados representados por funções.
    """
    if tokens is None:
        tokens = []
    else:
        tokens.clear()

    indice = 0
    parenteses = 0

    while indice < len(linha):
        token, indice = _estado_inicial(linha, indice)

        if token is None:
            break

        if token == "(":
            parenteses += 1
        elif token == ")":
            parenteses -= 1
            if parenteses < 0:
                raise ErroLexico("Parênteses desbalanceados")

        tokens.append(token)

    if parenteses != 0:
        raise ErroLexico("Parênteses desbalanceados")

    return tokens
