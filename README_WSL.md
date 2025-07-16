# **ARM-M4-Assembler-WSL**

**Cross-compile ARM Cortex-M4 assembly (`my_assembly.s`) using WSL Ubuntu on Windows and compare with custom assembler output (`my_assembly.bin`).**

## **Features**
- **Environment**: WSL Ubuntu on Windows.
- **Toolchain**: `gcc-arm-none-eabi` for ARM Cortex-M4.
- **Process**: Compile, link, convert to binary, disassemble with `objdump`, compare binaries.
- **VS Code**: Automate tasks in WSL.

## **Setup**
1. **Install WSL Ubuntu**:
   ```powershell
   wsl --install
   wsl -d Ubuntu
   sudo apt update && sudo apt upgrade -y
   ```
2. **Install ARM Toolchain**:
   ```bash
   sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi
   arm-none-eabi-gcc --version
   ```
3. **Set Up VS Code**:
   - Install [VS Code](https://code.visualstudio.com/download).
   - Install “Remote - WSL” extension.
   - Open project:
     ```bash
     cd ~/arm_assembler
     code .
     ```

## **Usage**
1. **Prepare `my_assembly.s`**:
   ```assembly
   .thumb
   .syntax unified
   .global _start
   _start:
       MOV R0, #10
       ADD R1, R0, #5
       SUB R2, R1, R0
       LDR R3, [R1, #4]
       STR R3, [R1, #8]
       B loop
   loop:
       BL subroutine
       BX LR
   subroutine:
       ADD R4, R3, R2
       BX LR
   ```
2. **Compile and Generate Binary**:
   ```bash
   arm-none-eabi-gcc -c -o my_assembly.o my_assembly.s
   arm-none-eabi-ld -Ttext=0x0 -o my_assembly.elf my_assembly.o
   arm-none-eabi-objcopy -O binary my_assembly.elf my_assembly_cross.bin
   ```
3. **Disassemble**:
   ```bash
   arm-none-eabi-objdump -d my_assembly.elf
   ```
4. **Compare Binaries**:
   ```bash
   diff -u <(xxd my_assembly.bin) <(xxd my_assembly_cross.bin)
   ```

