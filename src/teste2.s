@ ======================================================================
@ Codigo Assembly ARMv7 gerado automaticamente pelo compilador RPN
@ Plataforma: CPUlator DE1-SoC (v16.1)
@ Aritmetica: IEEE 754, 64 bits (double precision)
@ ======================================================================

.global _start

@ --- Secao de dados ---
.section .data

@ Constantes double (IEEE 754, codificadas como pares de .word)
    .align 3
const_0:  @ double 5.0
    .word 0x00000000
    .word 0x40140000
    .align 3
const_1:  @ double 3.0
    .word 0x00000000
    .word 0x40080000
    .align 3
const_10:  @ double 2.5
    .word 0x00000000
    .word 0x40040000
    .align 3
const_11:  @ double 3.5
    .word 0x00000000
    .word 0x400C0000
    .align 3
const_12:  @ double 1.5
    .word 0x00000000
    .word 0x3FF80000
    .align 3
const_2:  @ double 8.0
    .word 0x00000000
    .word 0x40200000
    .align 3
const_3:  @ double 2.0
    .word 0x00000000
    .word 0x40000000
    .align 3
const_4:  @ double 100.0
    .word 0x00000000
    .word 0x40590000
    .align 3
const_5:  @ double 10.0
    .word 0x00000000
    .word 0x40240000
    .align 3
const_6:  @ double 7
    .word 0x00000000
    .word 0x401C0000
    .align 3
const_7:  @ double 3
    .word 0x00000000
    .word 0x40080000
    .align 3
const_8:  @ double 2
    .word 0x00000000
    .word 0x40000000
    .align 3
const_9:  @ double 3.14
    .word 0x51EB851F
    .word 0x40091EB8

@ Constantes auxiliares
    .align 3
double_zero:
    .word 0x00000000
    .word 0x00000000
    .align 3
double_um:
    .word 0x00000000
    .word 0x3FF00000
    .align 3
double_milhao:
    .word 0x00000000
    .word 0x412E8480

@ Variaveis de memoria
    .align 3
mem_PI:
    .word 0x00000000
    .word 0x00000000

    .align 3
pilha_rpn:
    .space 1024

    .align 3
resultados:
    .space 96

    .align 2
print_buffer:
    .space 32

str_linha:
    .asciz "Linha "
    .align 2
str_doispontos:
    .asciz ": "
    .align 2
str_newline:
    .asciz "\n"
    .align 2
str_menos:
    .asciz "-"
    .align 2
str_ponto:
    .asciz "."
    .align 2
str_espaco:
    .asciz " "
    .align 2
str_fim:
    .asciz "\n=== FIM ===\n"
    .align 2

tabela_7seg:
    .word 0x3F, 0x06, 0x5B, 0x4F, 0x66
    .word 0x6D, 0x7D, 0x07, 0x7F, 0x6F

.equ LED_BASE,       0xFF200000
.equ HEX30_BASE,     0xFF200020
.equ HEX54_BASE,     0xFF200030
.equ SW_BASE,        0xFF200040
.equ BTN_BASE,       0xFF200050
.equ JTAG_UART_BASE, 0xFF201000

@ --- Secao de texto ---
.section .text

_start:
    @ ===== HABILITAR COPROCESSADOR VFP (ESSENCIAL) =====
    MRC p15, 0, R0, c1, c0, 2
    ORR R0, R0, #0x00F00000
    MCR p15, 0, R0, c1, c0, 2
    MOV R0, #0x40000000
    VMSR FPEXC, R0

    @ Inicializa ponteiros
    LDR R4, =pilha_rpn
    LDR R5, =resultados

    @ ========== Linha 0 ==========
    LDR R4, =pilha_rpn

    @ Push numero 5.0
    LDR R0, =const_0
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 3.0
    LDR R0, =const_1
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: +
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VADD.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 0
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #0
    VSTR.F64 D0, [R0]

    @ LEDs: linha 1
    LDR R0, =LED_BASE
    MOV R1, #1
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 0
    LDR R0, =resultados
    ADD R0, R0, #0
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 0: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #0
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #0
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 1 ==========
    LDR R4, =pilha_rpn

    @ Push numero 8.0
    LDR R0, =const_2
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 2.0
    LDR R0, =const_3
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: *
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VMUL.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 1
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #8
    VSTR.F64 D0, [R0]

    @ LEDs: linha 2
    LDR R0, =LED_BASE
    MOV R1, #2
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 1
    LDR R0, =resultados
    ADD R0, R0, #8
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 1: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #1
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #8
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 2 ==========
    LDR R4, =pilha_rpn

    @ RES 1 (resultado da linha 1)
    LDR R0, =resultados
    ADD R0, R0, #8
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 2
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #16
    VSTR.F64 D0, [R0]

    @ LEDs: linha 3
    LDR R0, =LED_BASE
    MOV R1, #3
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 2
    LDR R0, =resultados
    ADD R0, R0, #16
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 2: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #2
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #16
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 3 ==========
    LDR R4, =pilha_rpn

    @ RES 2 (resultado da linha 1)
    LDR R0, =resultados
    ADD R0, R0, #8
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 3
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #24
    VSTR.F64 D0, [R0]

    @ LEDs: linha 4
    LDR R0, =LED_BASE
    MOV R1, #4
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 3
    LDR R0, =resultados
    ADD R0, R0, #24
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 3: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #3
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #24
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 4 ==========
    LDR R4, =pilha_rpn

    @ Push numero 100.0
    LDR R0, =const_4
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 10.0
    LDR R0, =const_5
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: /
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VDIV.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 4
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #32
    VSTR.F64 D0, [R0]

    @ LEDs: linha 5
    LDR R0, =LED_BASE
    MOV R1, #5
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 4
    LDR R0, =resultados
    ADD R0, R0, #32
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 4: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #4
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #32
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 5 ==========
    LDR R4, =pilha_rpn

    @ Push numero 7
    LDR R0, =const_6
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 3
    LDR R0, =const_7
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: //
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    @ Divisao inteira
    VCVT.S32.F64 S0, D0
    VCVT.S32.F64 S2, D1
    VMOV R0, S0
    VMOV R1, S2
    PUSH {R4}
    BL div_inteira
    POP {R4}
    VMOV S4, R0
    VCVT.F64.S32 D2, S4
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 5
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #40
    VSTR.F64 D0, [R0]

    @ LEDs: linha 6
    LDR R0, =LED_BASE
    MOV R1, #6
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 5
    LDR R0, =resultados
    ADD R0, R0, #40
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 5: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #5
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #40
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 6 ==========
    LDR R4, =pilha_rpn

    @ Push numero 7
    LDR R0, =const_6
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 3
    LDR R0, =const_7
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: %
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    @ Resto da divisao inteira
    VCVT.S32.F64 S0, D0
    VCVT.S32.F64 S2, D1
    VMOV R0, S0
    VMOV R1, S2
    PUSH {R4}
    MOV R3, R0
    BL div_inteira
    MUL R2, R0, R1
    SUB R0, R3, R2
    POP {R4}
    VMOV S4, R0
    VCVT.F64.S32 D2, S4
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 6
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #48
    VSTR.F64 D0, [R0]

    @ LEDs: linha 7
    LDR R0, =LED_BASE
    MOV R1, #7
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 6
    LDR R0, =resultados
    ADD R0, R0, #48
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 6: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #6
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #48
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 7 ==========
    LDR R4, =pilha_rpn

    @ Push numero 5.0
    LDR R0, =const_0
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 2
    LDR R0, =const_8
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: ^
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    @ Potenciacao
    VCVT.S32.F64 S2, D1
    VMOV R1, S2
    PUSH {R4}
    BL potencia_func
    POP {R4}
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 7
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #56
    VSTR.F64 D0, [R0]

    @ LEDs: linha 8
    LDR R0, =LED_BASE
    MOV R1, #8
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 7
    LDR R0, =resultados
    ADD R0, R0, #56
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 7: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #7
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #56
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 8 ==========
    LDR R4, =pilha_rpn

    @ Push numero 3.14
    LDR R0, =const_9
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Store em memoria PI
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =mem_PI
    VSTR.F64 D0, [R0]
    @ Push o valor de volta
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 8
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #64
    VSTR.F64 D0, [R0]

    @ LEDs: linha 9
    LDR R0, =LED_BASE
    MOV R1, #9
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 8
    LDR R0, =resultados
    ADD R0, R0, #64
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 8: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #8
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #64
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 9 ==========
    LDR R4, =pilha_rpn

    @ Recall memoria PI
    LDR R0, =mem_PI
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 9
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #72
    VSTR.F64 D0, [R0]

    @ LEDs: linha 10
    LDR R0, =LED_BASE
    MOV R1, #10
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 9
    LDR R0, =resultados
    ADD R0, R0, #72
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 9: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #9
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #72
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 10 ==========
    LDR R4, =pilha_rpn

    @ Recall memoria PI
    LDR R0, =mem_PI
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 2.0
    LDR R0, =const_3
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: *
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VMUL.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 10
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #80
    VSTR.F64 D0, [R0]

    @ LEDs: linha 11
    LDR R0, =LED_BASE
    MOV R1, #11
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 10
    LDR R0, =resultados
    ADD R0, R0, #80
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 10: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #10
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #80
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ ========== Linha 11 ==========
    LDR R4, =pilha_rpn

    @ Push numero 2.5
    LDR R0, =const_10
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 3.5
    LDR R0, =const_11
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: +
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VADD.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8
    @ Push numero 1.5
    LDR R0, =const_12
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Push numero 2.0
    LDR R0, =const_3
    VLDR.F64 D0, [R0]
    VSTR.F64 D0, [R4]
    ADD R4, R4, #8
    @ Operacao: *
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VMUL.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8
    @ Operacao: -
    SUB R4, R4, #8
    VLDR.F64 D1, [R4]
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    VSUB.F64 D2, D0, D1
    VSTR.F64 D2, [R4]
    ADD R4, R4, #8

    @ Armazena resultado da linha 11
    SUB R4, R4, #8
    VLDR.F64 D0, [R4]
    LDR R0, =resultados
    ADD R0, R0, #88
    VSTR.F64 D0, [R0]

    @ LEDs: linha 12
    LDR R0, =LED_BASE
    MOV R1, #12
    STR R1, [R0]

    @ HEX: mostra parte inteira do resultado da linha 11
    LDR R0, =resultados
    ADD R0, R0, #88
    VLDR.F64 D0, [R0]
    VABS.F64 D1, D0
    VCVT.U32.F64 S4, D1
    VMOV R0, S4
    BL exibir_hex

    @ UART: imprime 'Linha 11: <resultado>'
    LDR R0, =str_linha
    BL uart_print_string
    MOV R0, #11
    BL uart_print_int
    LDR R0, =str_doispontos
    BL uart_print_string
    LDR R0, =resultados
    ADD R0, R0, #88
    VLDR.F64 D0, [R0]
    BL uart_print_double
    LDR R0, =str_newline
    BL uart_print_string

    @ LEDs: todos acesos = fim
    LDR R0, =LED_BASE
    LDR R1, =0x3FF
    STR R1, [R0]

    LDR R0, =str_fim
    BL uart_print_string

fim:
    B fim

@ ======================================================================
@ SUB-ROTINAS
@ ======================================================================

uart_print_char:
    PUSH {R1-R2, LR}
    LDR R1, =JTAG_UART_BASE
uart_wait:
    LDR R2, [R1, #4]
    LSR R2, R2, #16
    CMP R2, #0
    BEQ uart_wait
    STR R0, [R1]
    POP {R1-R2, PC}

uart_print_string:
    PUSH {R0-R1, LR}
    MOV R1, R0
ups_loop:
    LDRB R0, [R1], #1
    CMP R0, #0
    BEQ ups_done
    BL uart_print_char
    B ups_loop
ups_done:
    POP {R0-R1, PC}

uart_print_int:
    PUSH {R0-R5, LR}
    LDR R1, =print_buffer
    ADD R1, R1, #20
    MOV R2, #0
    STRB R2, [R1]
    MOV R3, R0
    CMP R3, #0
    BNE upi_loop
    SUB R1, R1, #1
    MOV R2, #48
    STRB R2, [R1]
    B upi_print
upi_loop:
    CMP R3, #0
    BEQ upi_print
    MOV R4, #10
    MOV R5, #0
    MOV R0, R3
upi_div:
    CMP R0, R4
    BLT upi_mod_done
    SUB R0, R0, R4
    ADD R5, R5, #1
    B upi_div
upi_mod_done:
    ADD R0, R0, #48
    SUB R1, R1, #1
    STRB R0, [R1]
    MOV R3, R5
    B upi_loop
upi_print:
    MOV R0, R1
    BL uart_print_string
    POP {R0-R5, PC}

uart_print_double:
    PUSH {R0-R6, LR}
    VPUSH {D0-D5}
    VMOV R0, R1, D0
    TST R1, #0x80000000
    BEQ upd_pos
    LDR R0, =str_menos
    BL uart_print_string
    VNEG.F64 D0, D0
upd_pos:
    VCVT.U32.F64 S10, D0
    VMOV R0, S10
    BL uart_print_int
    LDR R0, =str_ponto
    BL uart_print_string
    VCVT.F64.U32 D1, S10
    VSUB.F64 D2, D0, D1
    LDR R0, =double_milhao
    VLDR.F64 D3, [R0]
    VMUL.F64 D4, D2, D3
    VCVT.U32.F64 S10, D4
    VMOV R3, S10
    MOV R4, #6
    LDR R5, =100000
upd_dec_loop:
    CMP R4, #0
    BEQ upd_done
    MOV R0, R3
    MOV R1, R5
    MOV R2, #0
upd_dec_div:
    CMP R0, R1
    BLT upd_dec_div_done
    SUB R0, R0, R1
    ADD R2, R2, #1
    B upd_dec_div
upd_dec_div_done:
    MOV R3, R0
    ADD R0, R2, #48
    BL uart_print_char
    MOV R0, R5
    MOV R1, #10
    MOV R2, #0
upd_r5div:
    CMP R0, R1
    BLT upd_r5done
    SUB R0, R0, R1
    ADD R2, R2, #1
    B upd_r5div
upd_r5done:
    MOV R5, R2
    SUB R4, R4, #1
    B upd_dec_loop
upd_done:
    VPOP {D0-D5}
    POP {R0-R6, PC}

div_inteira:
    PUSH {R1-R5, LR}
    MOV R5, #0
    CMP R0, #0
    BGE di_a_pos
    RSB R0, R0, #0
    EOR R5, R5, #1
di_a_pos:
    CMP R1, #0
    BGE di_b_pos
    RSB R1, R1, #0
    EOR R5, R5, #1
di_b_pos:
    MOV R2, #0
di_loop:
    CMP R0, R1
    BLT di_fim
    SUB R0, R0, R1
    ADD R2, R2, #1
    B di_loop
di_fim:
    MOV R0, R2
    CMP R5, #1
    BNE di_ret
    RSB R0, R0, #0
di_ret:
    POP {R1-R5, PC}

potencia_func:
    PUSH {R1-R2, LR}
    VMOV.F64 D2, D0
    CMP R1, #0
    BNE pf_check1
    LDR R0, =double_um
    VLDR.F64 D2, [R0]
    POP {R1-R2, PC}
pf_check1:
    CMP R1, #1
    BEQ pf_fim
    VMOV.F64 D7, D0
    SUB R1, R1, #1
pf_loop:
    VMUL.F64 D2, D2, D7
    SUBS R1, R1, #1
    BNE pf_loop
pf_fim:
    POP {R1-R2, PC}

exibir_hex:
    PUSH {R0-R3, R7-R10, LR}
    MOV R7, R0
    MOV R10, #0
    MOV R8, #10
    BL mod_r7_r8
    LDR R1, =tabela_7seg
    LDR R0, [R1, R0, LSL #2]
    ORR R10, R10, R0
    MOV R0, R7
    MOV R1, #10
    BL div_simples
    MOV R7, R0
    MOV R8, #10
    BL mod_r7_r8
    LDR R1, =tabela_7seg
    LDR R0, [R1, R0, LSL #2]
    LSL R0, R0, #8
    ORR R10, R10, R0
    MOV R0, R7
    MOV R1, #10
    BL div_simples
    MOV R7, R0
    MOV R8, #10
    BL mod_r7_r8
    LDR R1, =tabela_7seg
    LDR R0, [R1, R0, LSL #2]
    LSL R0, R0, #16
    ORR R10, R10, R0
    MOV R0, R7
    MOV R1, #10
    BL div_simples
    MOV R7, R0
    MOV R8, #10
    BL mod_r7_r8
    LDR R1, =tabela_7seg
    LDR R0, [R1, R0, LSL #2]
    LSL R0, R0, #24
    ORR R10, R10, R0
    LDR R0, =HEX30_BASE
    STR R10, [R0]
    POP {R0-R3, R7-R10, PC}

mod_r7_r8:
    PUSH {R1-R2, LR}
    MOV R0, R7
    MOV R1, R8
mr8_loop:
    CMP R0, R1
    BLT mr8_fim
    SUB R0, R0, R1
    B mr8_loop
mr8_fim:
    POP {R1-R2, PC}

div_simples:
    PUSH {R1-R2, LR}
    MOV R2, #0
ds_loop:
    CMP R0, R1
    BLT ds_fim
    SUB R0, R0, R1
    ADD R2, R2, #1
    B ds_loop
ds_fim:
    MOV R0, R2
    POP {R1-R2, PC}

.end
