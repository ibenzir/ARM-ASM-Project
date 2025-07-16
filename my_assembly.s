; my_assembly.s
start:
    MOV R0, #10        ; Move 10 to R0
    ADD R1, R0, #5    ; Add 5 to R0, store in R1
    SUB R2, R1, R0    ; Subtract R0 from R1, store in R2
    LDR R3, [R1, #4]  ; Load from [R1 + 4] to R3
    STR R3, [R1, #8]  ; Store R3 to [R1 + 8]
    B loop            ; Branch to loop
loop:
    BL subroutine     ; Branch and link to subroutine
    BX LR             ; Return
subroutine:
    ADD R4, R3, R2    ; Add R3 and R2, store in R4
    BX LR             ; Return