@ Gerado automaticamente - compilador RPN -> ARMv7
@ CPUlator ARMv7 DEC1-SOC (v16.1)
.syntax unified
.cpu cortex-a9
.fpu vfpv3-d16

.section .data
const_0: .word 0x51EB851F, 0x40091EB8  @ 3.14
const_1: .word 0x00000000, 0x40000000  @ 2.0
res_line_0: .word 0, 0  @ resultado linha 0
const_2: .word 0x00000000, 0x40240000  @ 10.0
const_3: .word 0x00000000, 0x40160000  @ 5.5
res_line_1: .word 0, 0  @ resultado linha 1
const_4: .word 0x00000000, 0x40080000  @ 3.0
const_5: .word 0x00000000, 0x40100000  @ 4.0
res_line_2: .word 0, 0  @ resultado linha 2
const_6: .word 0x00000000, 0x401C0000  @ 7.0
const_7: .word 0x00000000, 0x40000000  @ 2.0
res_line_3: .word 0, 0  @ resultado linha 3
const_8: .word 0x00000000, 0x401C0000  @ 7
const_9: .word 0x00000000, 0x40000000  @ 2
res_line_4: .word 0, 0  @ resultado linha 4
const_10: .word 0x00000000, 0x401C0000  @ 7
const_11: .word 0x00000000, 0x40080000  @ 3
res_line_5: .word 0, 0  @ resultado linha 5
const_12: .word 0x00000000, 0x40000000  @ 2.0
const_13: .word 0x00000000, 0x40080000  @ 3
res_line_6: .word 0, 0  @ resultado linha 6
const_14: .word 0x00000000, 0x40454000  @ 42.5
var_VAL: .word 0, 0  @ VAL
res_line_8: .word 0, 0  @ resultado linha 8
const_15: .word 0x00000000, 0x3FF00000  @ 1
res_line_9: .word 0, 0  @ resultado linha 9
const_16: .word 0x00000000, 0x40080000  @ 3.0
const_17: .word 0x00000000, 0x40100000  @ 4.0
const_18: .word 0x00000000, 0x40000000  @ 2.0
const_19: .word 0x00000000, 0x40140000  @ 5.0
res_line_10: .word 0, 0  @ resultado linha 10
const_20: .word 0x00000000, 0x40000000  @ 2
res_line_11: .word 0, 0  @ resultado linha 11

.section .text
.global _start
_start:
    @ Habilita VFP
    MRC p15, 0, r0, c1, c0, 2
    ORR r0, r0, #0xF00000
    MCR p15, 0, r0, c1, c0, 2
    MOV r0, #0x40000000
    FMXR FPEXC, r0

line_0:  @ ( 3.14 2.0 + )
    LDR r0, =const_0
    VLDR.64 d2, [r0]
    LDR r0, =const_1
    VLDR.64 d3, [r0]
    VADD.F64 d4, d2, d3
    LDR r0, =res_line_0
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_1:  @ ( 10.0 5.5 - )
    LDR r0, =const_2
    VLDR.64 d2, [r0]
    LDR r0, =const_3
    VLDR.64 d3, [r0]
    VSUB.F64 d4, d2, d3
    LDR r0, =res_line_1
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_2:  @ ( 3.0 4.0 * )
    LDR r0, =const_4
    VLDR.64 d2, [r0]
    LDR r0, =const_5
    VLDR.64 d3, [r0]
    VMUL.F64 d4, d2, d3
    LDR r0, =res_line_2
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_3:  @ ( 7.0 2.0 / )
    LDR r0, =const_6
    VLDR.64 d2, [r0]
    LDR r0, =const_7
    VLDR.64 d3, [r0]
    VDIV.F64 d4, d2, d3
    LDR r0, =res_line_3
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_4:  @ ( 7 2 // )
    LDR r0, =const_8
    VLDR.64 d2, [r0]
    LDR r0, =const_9
    VLDR.64 d3, [r0]
    VDIV.F64 d4, d2, d3
    VCVT.S32.F64 s0, d4
    VCVT.F64.S32 d4, s0
    LDR r0, =res_line_4
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_5:  @ ( 7 3 % )
    LDR r0, =const_10
    VLDR.64 d2, [r0]
    LDR r0, =const_11
    VLDR.64 d3, [r0]
    VDIV.F64 d5, d2, d3
    VCVT.S32.F64 s0, d5
    VCVT.F64.S32 d5, s0
    VMUL.F64 d5, d5, d3
    VSUB.F64 d4, d2, d5
    LDR r0, =res_line_5
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_6:  @ ( 2.0 3 ^ )
    LDR r0, =const_12
    VLDR.64 d2, [r0]
    LDR r0, =const_13
    VLDR.64 d3, [r0]
    FCPYD d0, d2
    VCVT.S32.F64 s2, d3
    VMOV r1, s2
    BL pow_int
    FCPYD d4, d0
    LDR r0, =res_line_6
    VSTR.64 d4, [r0]
    FCPYD d0, d4
    BL print_double

line_7:  @ ( 42.5 VAL )
    LDR r0, =const_14
    VLDR.64 d2, [r0]
    LDR r0, =var_VAL
    VSTR.64 d2, [r0]

line_8:  @ ( VAL )
    LDR r0, =var_VAL
    VLDR.64 d2, [r0]
    LDR r0, =res_line_8
    VSTR.64 d2, [r0]
    FCPYD d0, d2
    BL print_double

line_9:  @ ( 1 RES )
    LDR r0, =const_15
    VLDR.64 d2, [r0]
    LDR r0, =res_line_8
    VLDR.64 d3, [r0]
    LDR r0, =res_line_9
    VSTR.64 d3, [r0]
    FCPYD d0, d3
    BL print_double

line_10:  @ ( ( 3.0 4.0 * ) ( 2.0 5.0 * ) + )
    LDR r0, =const_16
    VLDR.64 d2, [r0]
    LDR r0, =const_17
    VLDR.64 d3, [r0]
    VMUL.F64 d4, d2, d3
    LDR r0, =const_18
    VLDR.64 d5, [r0]
    LDR r0, =const_19
    VLDR.64 d6, [r0]
    VMUL.F64 d7, d5, d6
    VADD.F64 d8, d4, d7
    LDR r0, =res_line_10
    VSTR.64 d8, [r0]
    FCPYD d0, d8
    BL print_double

line_11:  @ ( 2 RES )
    LDR r0, =const_20
    VLDR.64 d2, [r0]
    LDR r0, =res_line_9
    VLDR.64 d3, [r0]
    LDR r0, =res_line_11
    VSTR.64 d3, [r0]
    FCPYD d0, d3
    BL print_double

_end:
    B _end

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
