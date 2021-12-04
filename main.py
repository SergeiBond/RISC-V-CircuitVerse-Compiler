# RISC-V ==> Circuitverse bytecode compiler
# v0.2
# By Sergei Bondarenko

from os.path import exists
import re



def itype(s):
    s = int(s) << 20        # push Imm
    return s | 0b0010011    # Opcode imprint

def rtype(s):
    return s | 0b0110011

def or_op(s):
    return s | 0b110000000000000

def and_op(s):
    return s | 0b111000000000000

def xor_op(s):
    return s | 0b100000000000000

def sub_op(s):
    return s | 0b01000000000000000000000000000000

def register(reg):
    if re.match('^[a][0-9]$|^[x][1-2][0-9]$|^[x]3[0-1]$', reg):
        return int(reg[1:])
    else:
        print(f"Invalid register name '{reg}'. Must be a0 ... a31.")
        exit(-31)

def rs1(s, reg):
    return s | (register(reg) << 15)

def rs2(s, reg):
    return s | (register(reg) << 20)

def rd(s, reg):
    return s | (register(reg) << 7)


def parse(name):
    print(f'Opening file {name}')

    if exists(name):
        with open(name, "r") as fd:
            lines = fd.read().splitlines()

            out = open("RISC_ASM_BYTECODE_UNIFIED.txt", "w")

            out_lo = open("RISC_ASM_BYTECODE_LO.txt", "w")

            out_hi = open("RISC_ASM_BYTECODE_HI.txt", "w")

            output_unary = []
            output_biary_lo = []
            output_biary_hi = []
            label_hash = {}

    else:
        print(f"File '{name}' does not exist. Check if the name is spelled correctly and the file is present in the script`s directory.")
        exit(-2)


    rtype_list = ['add', 'sub', 'xor', 'or', 'and']
    itype_list = ['addi', 'xori', 'ori', 'andi']

    # Magna Schema

    # int('11111111', 2)

    # bin(0b000000001111 << 20) # Push Immediate to the end

    # Splitting
    # (0b00000000001000010000000100010011 ) & 0xffff        # 0-15
    # (0b00000000001000010000000100010011 >> 16) & 0xffff   # 16-31

    idx = 0
    i = 0
    preprocessed = []

    while i < len(lines):
        lines[i] = lines[i].replace(',', ' ')
        instruction = [a for a in lines[i].split() if a]
        if instruction[0][-1] == ':':
            label_hash[instruction[0][:-1]] = idx
            if len(instruction) == 1:
                i += 1
            else:
                preprocessed.append(instruction[1:])
                idx += 1
                i += 1
        else:
            preprocessed.append(instruction)
            idx += 1
            i += 1



    for instruction in preprocessed:
        opcode = 0

        if instruction[0] in itype_list:
            opcode = itype(instruction[3])
            if instruction[0] == 'ori':
                opcode = or_op(opcode)
            elif instruction[0] == 'andi':
                opcode = and_op(opcode)
            elif instruction[0] == 'xori':
                opcode = xor_op(opcode)
            elif instruction[0] == 'addi':
                pass    # addi func3 is 000
            else:
                print("Illegal I-Type instruction")
                exit(-11)

            opcode = rd(opcode, instruction[1])
            opcode = rs1(opcode, instruction[2])

        elif instruction[0] in rtype_list:
            opcode = rtype(opcode)
            if instruction[0] == 'or':
                opcode = or_op(opcode)
            elif instruction[0] == 'and':
                opcode = and_op(opcode)
            elif instruction[0] == 'xor':
                opcode = xor_op(opcode)
            elif instruction[0] == 'add':
                pass  # addi func3 is 000
            elif instruction[0] == 'sub':
                opcode = sub_op(opcode)
            else:
                print("Illegal R-Type instruction")
                exit(-22)

            opcode = rd(opcode, instruction[1])
            opcode = rs1(opcode, instruction[2])
            opcode = rs2(opcode, instruction[3])


        output_unary.append(opcode)
        output_biary_lo.append(opcode & 0xffff)
        output_biary_hi.append((opcode >> 16) & 0xffff)

    output_unary_str = [str(i) for i in output_unary]
    out.write(','.join(output_unary_str))

    output_biary_lo_str = [str(i) for i in output_biary_lo]
    out_lo.write(','.join(output_biary_lo_str))

    output_biary_hi_str = [str(i) for i in output_biary_hi]
    out_hi.write(','.join(output_biary_hi_str))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    filename = input("Enter the name of your file: ")
    parse(filename)
