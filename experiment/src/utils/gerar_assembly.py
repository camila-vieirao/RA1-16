"""
utils.py - logica de geracao de Assembly ARMv7 a partir de tokens RPN.

Compativel com CPUlator ARMv7 DEC1-SOC (v16.1).
Nenhum calculo aritmetico da linguagem RPN ocorre em Python.
"""

import struct

# Estado global
data_lines    = []
text_lines    = []
const_counter = 0
label_counter = 0
mem_vars      = {}
res_labels    = {}
current_line  = 0


def reset_state():
    global data_lines, text_lines, const_counter, label_counter
    global mem_vars, res_labels, current_line
    data_lines    = []
    text_lines    = []
    const_counter = 0
    label_counter = 0
    mem_vars      = {}
    res_labels    = {}
    current_line  = 0


def double_to_words(value):
    """Representacao IEEE 754 double little-endian — nao e calculo RPN."""
    packed = struct.pack('<d', float(value))
    lo, hi = struct.unpack('<II', packed)
    return f"0x{lo:08X}", f"0x{hi:08X}"


def emit_data(line): data_lines.append(line)
def emit(line):      text_lines.append(line)


def alloc_reg(next_reg):
    r = next_reg[0]
    if r > 15:
        raise RuntimeError("Registradores VFP esgotados.")
    next_reg[0] += 1
    return r


def is_number(tok):
    try: float(tok); return True
    except ValueError: return False

def is_operator(tok):
    return tok in {"+", "-", "*", "/", "//", "%", "^"}

def is_mem_name(tok):
    return tok != "RES" and len(tok) > 0 and tok.isalpha() and tok.isupper()


def load_const(tok, next_reg):
    global const_counter
    lo, hi = double_to_words(float(tok))
    label = f"const_{const_counter}"; const_counter += 1
    emit_data(f"{label}: .word {lo}, {hi}  @ {tok}")
    reg = alloc_reg(next_reg)
    emit(f"    LDR r0, ={label}")
    emit(f"    VLDR.64 d{reg}, [r0]")
    return reg


def emit_binop(op, ra, rb, next_reg):
    rd = alloc_reg(next_reg)
    if op == "+":
        emit(f"    VADD.F64 d{rd}, d{ra}, d{rb}")
    elif op == "-":
        emit(f"    VSUB.F64 d{rd}, d{ra}, d{rb}")
    elif op == "*":
        emit(f"    VMUL.F64 d{rd}, d{ra}, d{rb}")
    elif op == "/":
        emit(f"    VDIV.F64 d{rd}, d{ra}, d{rb}")
    elif op == "//":
        emit(f"    VDIV.F64 d{rd}, d{ra}, d{rb}")
        emit(f"    VCVT.S32.F64 s0, d{rd}")
        emit(f"    VCVT.F64.S32 d{rd}, s0")
    elif op == "%":
        tmp = alloc_reg(next_reg)
        emit(f"    VDIV.F64 d{tmp}, d{ra}, d{rb}")
        emit(f"    VCVT.S32.F64 s0, d{tmp}")
        emit(f"    VCVT.F64.S32 d{tmp}, s0")
        emit(f"    VMUL.F64 d{tmp}, d{tmp}, d{rb}")
        emit(f"    VSUB.F64 d{rd}, d{ra}, d{tmp}")
    elif op == "^":
        emit(f"    FCPYD d0, d{ra}")
        emit(f"    VCVT.S32.F64 s2, d{rb}")
        emit(f"    VMOV r1, s2")
        emit(f"    BL pow_int")
        emit(f"    FCPYD d{rd}, d0")
    else:
        emit(f"    @ AVISO: operador desconhecido '{op}'")
    return rd


def emit_mem_store(name, val_reg):
    if name not in mem_vars:
        label = f"var_{name}"; mem_vars[name] = label
        emit_data(f"{label}: .word 0, 0  @ {name}")
    emit(f"    LDR r0, ={mem_vars[name]}")
    emit(f"    VSTR.64 d{val_reg}, [r0]")


def emit_mem_load(name, next_reg):
    if name not in mem_vars:
        label = f"var_{name}"; mem_vars[name] = label
        lo, hi = double_to_words(0.0)
        emit_data(f"{label}: .word {lo}, {hi}  @ {name} nao inicializada = 0.0")
    reg = alloc_reg(next_reg)
    emit(f"    LDR r0, ={mem_vars[name]}")
    emit(f"    VLDR.64 d{reg}, [r0]")
    return reg


def emit_res_load(n, next_reg):
    global label_counter
    target = current_line - n
    reg = alloc_reg(next_reg)
    if target < 0 or target not in res_labels:
        lo, hi = double_to_words(0.0)
        zlabel = f"zero_res_{label_counter}"; label_counter += 1
        emit_data(f"{zlabel}: .word {lo}, {hi}  @ RES({n}) invalido = 0.0")
        emit(f"    LDR r0, ={zlabel}")
    else:
        emit(f"    LDR r0, ={res_labels[target]}")
    emit(f"    VLDR.64 d{reg}, [r0]")
    return reg


def process_tokens(tokens, next_reg):
    res_n_map = {}
    for idx, tok in enumerate(tokens):
        if tok == "RES":
            for k in range(idx - 1, -1, -1):
                if is_number(tokens[k]):
                    res_n_map[idx] = int(float(tokens[k])); break

    frame_stack = []
    root_regs   = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            frame_stack.append({'op': None, 'operands': [], 'is_store': False})
        elif tok == ")":
            if not frame_stack:
                i += 1; continue
            frame = frame_stack.pop()
            result = None
            if frame['is_store']:
                pass
            elif frame['op'] is None and len(frame['operands']) == 1:
                result = frame['operands'][0]
            elif frame['op'] and len(frame['operands']) >= 2:
                result = emit_binop(frame['op'], frame['operands'][0], frame['operands'][1], next_reg)
            elif frame['operands']:
                result = frame['operands'][0]
            if result is not None:
                (frame_stack[-1]['operands'] if frame_stack else root_regs).append(result)
        elif is_number(tok):
            reg = load_const(tok, next_reg)
            (frame_stack[-1]['operands'] if frame_stack else root_regs).append(reg)
        elif is_operator(tok):
            if frame_stack: frame_stack[-1]['op'] = tok
        elif tok == "RES":
            n = res_n_map.get(i, 1)
            if frame_stack and frame_stack[-1]['operands']:
                frame_stack[-1]['operands'].pop()
            reg = emit_res_load(n, next_reg)
            if frame_stack:
                frame_stack[-1]['operands'].append(reg)
                frame_stack[-1]['op'] = None
            else:
                root_regs.append(reg)
        elif is_mem_name(tok):
            if frame_stack:
                frame = frame_stack[-1]
                if frame['operands']:
                    emit_mem_store(tok, frame['operands'][0])
                    frame.update({'is_store': True, 'operands': [], 'op': None})
                else:
                    reg = emit_mem_load(tok, next_reg)
                    frame['operands'].append(reg)
            else:
                root_regs.append(emit_mem_load(tok, next_reg))
        else:
            emit(f"    @ AVISO: token desconhecido '{tok}'")
        i += 1
    return root_regs[-1] if root_regs else None


# 100.0 em IEEE 754 double: 0x4059000000000000
# lo=0x00000000, hi=0x40590000
SUBROUTINES = """\
.section .data
hex_seg_table: .byte 0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x6F
.align 2                              @ alinha para 4 bytes apos os 10 bytes da tabela
pow_one_const: .word 0x00000000, 0x3FF00000  @ 1.0 IEEE 754
_const_100:   .word 0x00000000, 0x40590000  @ 100.0 IEEE 754

.section .text

@ ---------------------------------------------------------------
@ _div10: divide r0 por 10 (software, sem UDIV).
@ Entrada: r0 = dividendo (nao negativo)
@ Saida:   r0 = quociente, r1 = resto
@ ---------------------------------------------------------------
_div10:
    PUSH {r2, lr}
    MOV r1, r0
    MOV r0, #0
_div10_loop:
    CMP r1, #10
    BLT _div10_done
    SUB r1, r1, #10
    ADD r0, r0, #1
    B _div10_loop
_div10_done:
    POP {r2, lr}
    BX lr

@ ---------------------------------------------------------------
@ print_double: exibe d0 na UART (0xFF201000) e HEX displays.
@ Formato: [-]NNNN.DD  (2 casas decimais)
@
@ Usa: VPUSH/VPOP d1 para preservar registrador VFP.
@ r4-r7 salvos/restaurados.
@ ---------------------------------------------------------------
print_double:
    PUSH {r4, r5, r6, r7, r8, lr}   @ 6 regs = 24 bytes, stack permanece 8-byte aligned
    VPUSH {d1}

    @ salva d0 original em d1
    FCPYD d1, d0

    @ parte inteira em r5
    VCVT.S32.F64 s0, d0
    VMOV r5, s0

    LDR r6, =0xFF201000      @ UART (permanente em r6)
    LDR r7, =hex_seg_table   @ tabela 7-seg (permanente em r7)

    @ --- UART: sinal e parte inteira ---
    MOV r0, r5
    CMP r0, #0
    BGE _pd_pos
    MOV r4, #0x2D
    STR r4, [r6]             @ '-'
    RSB r0, r0, #0           @ abs
_pd_pos:
    CMP r0, #0
    BNE _pd_nz
    MOV r4, #0x30
    STR r4, [r6]             @ '0'
    B _pd_dec
_pd_nz:
    MOV r4, #0               @ contador de digitos
_pd_push:
    CMP r0, #0
    BEQ _pd_pop
    BL _div10                @ r0=quociente, r1=resto (digito)
    ADD r1, r1, #0x30
    PUSH {r1}
    ADD r4, r4, #1
    B _pd_push
_pd_pop:
    CMP r4, #0
    BEQ _pd_dec
    POP {r1}
    STR r1, [r6]
    SUB r4, r4, #1
    B _pd_pop

    @ --- UART: parte decimal (2 digitos) ---
_pd_dec:
    MOV r4, #0x2E
    STR r4, [r6]             @ '.'

    @ d0 = (double) parte inteira
    VMOV s0, r5
    VCVT.F64.S32 d0, s0

    @ d1 = d1 - d0 = parte fracionaria
    VSUB.F64 d1, d1, d0

    @ garante positivo
    CMP r5, #0
    BGE _pd_frac_pos
    VNEG.F64 d1, d1
_pd_frac_pos:
    @ d0 = 100.0, d1 = frac * 100
    LDR r0, =_const_100
    VLDR.64 d0, [r0]
    VMUL.F64 d1, d1, d0

    @ extrai 2 digitos decimais
    VCVT.S32.F64 s0, d1
    VMOV r0, s0              @ r0 = 0..99
    BL _div10                @ r0=dezena, r1=unidade
    ADD r4, r0, #0x30
    STR r4, [r6]             @ dezena
    ADD r4, r1, #0x30
    STR r4, [r6]             @ unidade

    MOV r4, #0x0A
    STR r4, [r6]             @ newline

    @ --- HEX displays: parte inteira (6 digitos) ---
    MOV r0, r5
    CMP r0, #0
    RSBLT r0, r0, #0         @ abs
    MOV r3, #0               @ word HEX3-HEX0
    MOV r4, #0               @ word HEX5-HEX4

    BL _div10
    LDRB r1, [r7, r1]
    ORR r3, r3, r1

    BL _div10
    LDRB r1, [r7, r1]
    ORR r3, r3, r1, LSL #8

    BL _div10
    LDRB r1, [r7, r1]
    ORR r3, r3, r1, LSL #16

    BL _div10
    LDRB r1, [r7, r1]
    ORR r3, r3, r1, LSL #24

    BL _div10
    LDRB r1, [r7, r1]
    ORR r4, r4, r1

    BL _div10
    LDRB r1, [r7, r1]
    ORR r4, r4, r1, LSL #8

    LDR r0, =0xFF200020
    STR r3, [r0]
    LDR r0, =0xFF200030
    STR r4, [r0]

    VPOP {d1}
    POP {r4, r5, r6, r7, r8, lr}
    BX lr

@ ---------------------------------------------------------------
@ pow_int: d0^r1 (r1 inteiro >= 0). Resultado em d0.
@ ---------------------------------------------------------------
pow_int:
    PUSH {r1, r2, lr}
    LDR r2, =pow_one_const
    VLDR.64 d1, [r2]
_pi_loop:
    CMP r1, #0
    BEQ _pi_done
    VMUL.F64 d1, d1, d0
    SUB r1, r1, #1
    B _pi_loop
_pi_done:
    FCPYD d0, d1
    POP {r1, r2, lr}
    BX lr
"""


def gerar_linha_assembly(tokens, codigoAssembly):
    global current_line
    next_reg = [2]
    emit(f"line_{current_line}:  @ {' '.join(tokens)}")
    result = process_tokens(tokens, next_reg)
    if result is not None:
        lbl = f"res_line_{current_line}"
        res_labels[current_line] = lbl
        emit_data(f"{lbl}: .word 0, 0  @ resultado linha {current_line}")
        emit(f"    LDR r0, ={lbl}")
        emit(f"    VSTR.64 d{result}, [r0]")
        emit(f"    FCPYD d0, d{result}")
        emit("    BL print_double")
    emit("")
    codigoAssembly += text_lines[:]
    current_line += 1


def build_assembly():
    lines = [
        "@ Gerado automaticamente - compilador RPN -> ARMv7",
        "@ CPUlator ARMv7 DEC1-SOC (v16.1)",
        ".syntax unified", ".cpu cortex-a9", ".fpu vfpv3-d16", "",
        ".section .data",
    ]
    lines += data_lines
    lines += [
        "", ".section .text", ".global _start", "_start:",
        "    @ Habilita VFP",
        "    MRC p15, 0, r0, c1, c0, 2",
        "    ORR r0, r0, #0xF00000",
        "    MCR p15, 0, r0, c1, c0, 2",
        "    MOV r0, #0x40000000",
        "    FMXR FPEXC, r0", "",
    ]
    lines += text_lines
    lines += ["_end:", "    B _end", "", SUBROUTINES]
    return "\n".join(lines)
