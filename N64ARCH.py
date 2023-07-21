from binaryninja.log import *
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import InstructionTextTokenType, BranchType


import rabbitizer
import re


def parse_instruction_string(instruction_string):
    if ' . + 4' in instruction_string:
        instruction_string = instruction_string.replace(' . + 4 + (', ' ')
        instruction_string = instruction_string.replace(' << 2)', '')
    if 'func' in instruction_string:
        instruction_string = instruction_string.replace('func_8', '0x')
    instruction1 = instruction_string.split()
    instruction2 = [instruction1[0]]
    if len(instruction1) > 1:
        instruction2.append(instruction_string[len(instruction1[0])+1:instruction_string.find(instruction1[1])])
        for i in range(1, len(instruction1)):
            if instruction1[i].endswith(','):
                instruction1[i] = instruction1[i][:-1]
                instruction2.append(instruction1[i])
                instruction2.append(', ')
            elif instruction1[i].endswith(')'):
                instruction2.append(instruction1[i][0:instruction1[i].find('(')])
                instruction2.append('(')
                instruction2.append(instruction1[i][instruction1[i].find('(')+1:-1])
                instruction2.append(')')
            else:
                instruction2.append(instruction1[i])
    return instruction2

def get_instruction(word):
    return parse_instruction_string(rabbitizer.Instruction(int.from_bytes(word, 'big', signed=False)).disassemble())


class N64(Architecture):
    name = 'N64'
    address_size = 4
    default_int_size = 1
    instr_alignment = 4
    max_instr_length = 4

    # Register Information
    regs = {
        # 'R0': 0,
        'AT': RegisterInfo('AT', 8),
        'V0': RegisterInfo('V0', 8),
        'V1': RegisterInfo('V1', 8),
        'A0': RegisterInfo('A0', 8),
        'A1': RegisterInfo('A1', 8),
        'A2': RegisterInfo('A2', 8),
        'A3': RegisterInfo('A3', 8),
        'T0': RegisterInfo('T0', 8),
        'T1': RegisterInfo('T1', 8),
        'T2': RegisterInfo('T2', 8),
        'T3': RegisterInfo('T3', 8),
        'T4': RegisterInfo('T4', 8),
        'T5': RegisterInfo('T5', 8),
        'T6': RegisterInfo('T6', 8),
        'T7': RegisterInfo('T7', 8),
        'S0': RegisterInfo('S0', 8),
        'S1': RegisterInfo('S1', 8),
        'S2': RegisterInfo('S2', 8),
        'S3': RegisterInfo('S3', 8),
        'S4': RegisterInfo('S4', 8),
        'S5': RegisterInfo('S5', 8),
        'S6': RegisterInfo('S6', 8),
        'S7': RegisterInfo('S7', 8),
        'T8': RegisterInfo('T8', 8),
        'T9': RegisterInfo('T9', 8),
        'K0': RegisterInfo('K0', 8),
        'K1': RegisterInfo('K1', 8),
        'GP': RegisterInfo('GP', 8),
        'SP': RegisterInfo('SP', 8),
        'FP': RegisterInfo('FP', 8),
        'RA': RegisterInfo('RA', 8),
        'F0': RegisterInfo('F0', 8),
        'F1': RegisterInfo('F1', 8),
        'F2': RegisterInfo('F2', 8),
        'F3': RegisterInfo('F3', 8),
        'F4': RegisterInfo('F4', 8),
        'F5': RegisterInfo('F5', 8),
        'F6': RegisterInfo('F6', 8),
        'F7': RegisterInfo('F7', 8),
        'F8': RegisterInfo('F8', 8),
        'F9': RegisterInfo('F9', 8),
        'F10': RegisterInfo('F10', 8),
        'F11': RegisterInfo('F11', 8),
        'F12': RegisterInfo('F12', 8),
        'F13': RegisterInfo('F13', 8),
        'F14': RegisterInfo('F14', 8),
        'F15': RegisterInfo('F15', 8),
        'F16': RegisterInfo('F16', 8),
        'F17': RegisterInfo('F17', 8),
        'F18': RegisterInfo('F18', 8),
        'F19': RegisterInfo('F19', 8),
        'F20': RegisterInfo('F20', 8),
        'F21': RegisterInfo('F21', 8),
        'F22': RegisterInfo('F22', 8),
        'F23': RegisterInfo('F23', 8),
        'F24': RegisterInfo('F24', 8),
        'F25': RegisterInfo('F25', 8),
        'F26': RegisterInfo('F26', 8),
        'F27': RegisterInfo('F27', 8),
        'F28': RegisterInfo('F28', 8),
        'F29': RegisterInfo('F29', 8),
        'F30': RegisterInfo('F30', 8),
        'COP0S': RegisterInfo('COP0S', 4),
        'COP0C': RegisterInfo('COP0C', 8),
        'COP1': RegisterInfo('COP1', 4),
    }
    stack_pointer = 'SP'

    def get_instruction_info(self, data, addr):
        result = InstructionInfo()
        instruction = get_instruction(data)
        if instruction[0] == 'b':
            result.add_branch(BranchType.UnconditionalBranch, addr + 4 * int(instruction[-1], 16))
        elif instruction[0].startswith('b') and instruction[0] != 'break':
            result.add_branch(BranchType.TrueBranch, addr + 4 * int(instruction[-1], 16))
            result.add_branch(BranchType.FalseBranch, addr + 4)
        elif instruction[0] in ['j', 'jal']:
            result.add_branch(BranchType.UnconditionalBranch, (addr & 0xF0000000) | (int(instruction[-1][6:], 16) << 2))
        elif instruction[0] in ['jr', 'jalr']:
            result.add_branch(BranchType.IndirectBranch)

        result.length = 4
        return result

    def get_instruction_text(self, data, addr):
        instruction = get_instruction(data)
        tokens = []
        tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, instruction[0]))
        for i in range(1, len(instruction)):
            if instruction[i] == ', ':
                tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, instruction[i]))
            elif instruction[i].startswith(' '):
                tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, instruction[i]))
            elif instruction[i].startswith('$') or instruction[i] in ['TagHi', 'TagLo', 'Compare', 'Count', 'Cause']:
                tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, instruction[i]))
            elif instruction[i].startswith('0x') or instruction[i].startswith('-0x'):
                tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, instruction[i]))
            elif instruction[i] == '(' or instruction[i] == ')':
                tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, instruction[i]))
            elif instruction[i].isdigit():
                tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, instruction[i]))
            else:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, instruction[i]))
                log_error(f'Unrecognized token: {instruction[i]} in {instruction}')
        return tokens, 4

    def get_instruction_low_level_il(self, data, addr, il):
        return None
