# ARM Cortex-M4 Assembler

**A Python-based assembler for ARM Cortex-M4 (Thumb-2) that converts `my_assembly.s` to `my_assembly.bin`.**

## **Features**
- **Supports**: Data Processing (`ADD`, `SUB`, `MOV`), Data Transfer (`LDR`, `STR`), Branch (`B`, `BL`, `BX`).
- **Input**: Assembly file (`my_assembly.s`).
- **Output**: Binary file (`my_assembly.bin`).
- **Environment**: Visual Studio Code with Python 3.

## **Setup**
1. **Install VS Code**: [Download](https://code.visualstudio.com/download).
2. **Install Python 3**:
   ```bash
   python3 --version
   ```
3. **Clone Repository**:
   ```bash
   git clone https://github.com/ibenzir/ARM-ASM-Project.git
   cd arm-assembler
   ```

## **Usage**
1. **Create `my_assembly.s`**:
   ```assembly
   ; my_assembly.s
   start:
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
2. **Run Assembler**:
   ```bash
   python3 assembler.py my_assembly.s my_assembly.bin
   ```
3. **Verify Output** (For Windows OS):
   ```bash
   Format-Hex my_assembly.bin
   ```

## **VS Code Automation**
- **Create `.vscode/tasks.json`**:
  ```json
  {
      "version": "2.0.0",
      "tasks": [
          {
              "label": "Assemble",
              "type": "shell",
              "command": "python3 assembler.py my_assembly.s my_assembly.bin",
              "group": {"kind": "build", "isDefault": true}
          }
      ]
  }
  ```
- **Run Task**: `Ctrl + Shift + P` > “Tasks: Run Task” > “Assemble”.

- **For Cross Platform**: [Read This](https://github.com/ibenzir/ARM-ASM-Project/blob/main/README_WSL.md).
