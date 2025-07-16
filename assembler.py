# assembler.py
import re
import struct
import sys

# Instruction opcodes for ARM Cortex-M4 (Thumb-2)
OPCODES = {
    # Data Processing (16-bit and 32-bit Thumb-2)
    'ADD': {'reg_reg': 0x1800, 'reg_imm': 0xF1000000},  # ADD Rd, Rn, Rm; ADD Rd, Rn, #imm
    'SUB': {'reg_reg': 0x1A00, 'reg_imm': 0xF1A00000},  # SUB Rd, Rn, Rm; SUB Rd, Rn, #imm
    'MOV': {'reg_imm': 0xF04F0000},                     # MOV Rd, #imm
    # Data Transfer (32-bit)
    'LDR': {'reg_offset': 0xF8500000},                  # LDR Rt, [Rn, #offset]
    'STR': {'reg_offset': 0xF8400000},                  # STR Rt, [Rn, #offset]
    # Branch
    'B':   {'label': 0xE0000000},                       # B label (32-bit)
    'BL':  {'label': 0xF0009000},                       # BL label (32-bit)
    'BX':  {'reg': 0x4700},                            # BX Rm (16-bit)
}

# Regular expressions for parsing instructions
INSTRUCTION_PATTERNS = {
    r'ADD\s+R(\d+),\s*R(\d+),\s*R(\d+)': ('ADD', 'reg_reg'),
    r'ADD\s+R(\d+),\s*R(\d+),\s*#(\d+)': ('ADD', 'reg_imm'),
    r'SUB\s+R(\d+),\s*R(\d+),\s*R(\d+)': ('SUB', 'reg_reg'),
    r'SUB\s+R(\d+),\s*R(\d+),\s*#(\d+)': ('SUB', 'reg_imm'),
    r'MOV\s+R(\d+),\s*#(\d+)': ('MOV', 'reg_imm'),
    r'LDR\s+R(\d+),\s*\[R(\d+)(?:,\s*#(\d+))?\]': ('LDR', 'reg_offset'),
    r'STR\s+R(\d+),\s*\[R(\d+)(?:,\s*#(\d+))?\]': ('STR', 'reg_offset'),
    r'B\s+(\w+)': ('B', 'label'),
    r'BL\s+(\w+)': ('BL', 'label'),
    r'BX\s+R(\d+)': ('BX', 'reg'),
}

def parse_assembly(file_path):
    labels = {}
    instructions = []
    address = 0

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

    # First pass: Collect labels
    for line in lines:
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        if line.endswith(':'):
            label = line[:-1]
            labels[label] = address
            print(f"Label found: {label} at address 0x{address:04x}")
        else:
            # Assume 4 bytes for 32-bit, 2 bytes for 16-bit (BX)
            address += 2 if 'BX' in line.upper() else 4

    # Second pass: Parse instructions
    address = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith(';') or line.endswith(':'):
            continue
        for pattern, (opcode_name, variant) in INSTRUCTION_PATTERNS.items():
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                instructions.append((address, opcode_name, variant, match.groups()))
                print(f"Parsed: {line} -> {opcode_name} {variant} {match.groups()}")
                address += 2 if opcode_name == 'BX' else 4
                break
        else:
            print(f"Warning: Unknown instruction: {line}")
            continue

    return labels, instructions

def encode_instruction(opcode_name, variant, args, labels, current_address):
    opcode = OPCODES[opcode_name][variant]
    try:
        if opcode_name in ['ADD', 'SUB']:
            if variant == 'reg_reg':
                rd, rn, rm = map(int, args)
                if rd > 7 or rn > 7 or rm > 7:  # 16-bit Thumb limits
                    raise ValueError("Register out of range for 16-bit encoding")
                # 16-bit Thumb encoding: ADD/SUB Rd, Rn, Rm
                machine_code = opcode | (rn << 3) | (rm << 0) | (rd << 8)
                print(f"Encoded {opcode_name} reg_reg: 0x{machine_code:04x}")
                return machine_code, 2
            elif variant == 'reg_imm':
                rd, rn, imm = map(int, args)
                if imm > 0xFF:  # Simplified immediate range
                    raise ValueError("Immediate value too large")
                # 32-bit Thumb-2 encoding: ADD/SUB Rd, Rn, #imm
                machine_code = opcode | (rn << 16) | (rd << 8) | (imm & 0xFF)
                print(f"Encoded {opcode_name} reg_imm: 0x{machine_code:08x}")
                return machine_code, 4
        elif opcode_name == 'MOV':
            rd, imm = map(int, args)
            if imm > 0xFF:
                raise ValueError("Immediate value too large")
            # 32-bit Thumb-2 encoding: MOV Rd, #imm
            machine_code = opcode | (rd << 8) | (imm & 0xFF)
            print(f"Encoded MOV reg_imm: 0x{machine_code:08x}")
            return machine_code, 4
        elif opcode_name in ['LDR', 'STR']:
            rt, rn, offset = args
            offset = int(offset) if offset else 0
            if offset > 0xFFF:
                raise ValueError("Offset too large")
            # 32-bit Thumb-2 encoding: LDR/STR Rt, [Rn, #offset]
            machine_code = opcode | (int(rn) << 16) | (int(rt) << 12) | (offset & 0xFFF)
            print(f"Encoded {opcode_name} reg_offset: 0x{machine_code:08x}")
            return machine_code, 4
        elif opcode_name in ['B', 'BL']:
            label = args[0]
            target_address = labels.get(label)
            if target_address is None:
                raise ValueError(f"Undefined label: {label}")
            offset = target_address - (current_address + 4)
            offset = offset >> 1  # Thumb-2 offset is word-aligned
            if abs(offset) > 0x7FFFFF:
                raise ValueError("Branch offset too large")
            # Simplified 32-bit branch encoding
            machine_code = opcode | (offset & 0x7FFFFF)
            print(f"Encoded {opcode_name} label: 0x{machine_code:08x}")
            return machine_code, 4
        elif opcode_name == 'BX':
            rm = int(args[0])
            if rm > 15:
                raise ValueError("Register out of range for BX")
            # 16-bit Thumb encoding: BX Rm
            machine_code = opcode | (rm << 3)
            print(f"Encoded BX reg: 0x{machine_code:04x}")
            return machine_code, 2
    except Exception as e:
        print(f"Error encoding {opcode_name} {variant}: {e}")
        return 0, 0
    return 0, 0

def assemble(file_path, output_path):
    labels, instructions = parse_assembly(file_path)
    if not instructions:
        print("No instructions to assemble. Output file will be empty.")
        return

    with open(output_path, 'wb') as f:
        for address, opcode_name, variant, args in instructions:
            machine_code, length = encode_instruction(opcode_name, variant, args, labels, address)
            if machine_code == 0:
                print(f"Skipping invalid instruction at address 0x{address:04x}")
                continue
            if length == 4:
                f.write(struct.pack('<I', machine_code))  # Write 32-bit
            else:
                f.write(struct.pack('<H', machine_code))  # Write 16-bit
            print(f"Wrote 0x{machine_code:0{length*2}x} to {output_path} at offset 0x{f.tell()-length:04x}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python assembler.py input.s output.bin")
        sys.exit(1)
    assemble(sys.argv[1], sys.argv[2])