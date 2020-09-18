"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
SUB = 0b10100001
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.running = True
        self.reg[7] = 0xF4
        self.fl = [False] * 8


    def load(self):
        """Load a program into memory."""

        address = 0
        with open(sys.argv[1]) as files:
            for line in files:
                split = line.split('#')
                command = split[0].strip()
                if command == '':
                    continue
                if command[0] == '1' or command[0] == '0':
                    num = command[:8]
                    self.ram[address] = int(num, 2)
                    address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "CMP":
            equal = self.fl[7]
            greaterThan = self.fl[6]
            lessThan = self.fl[5]
            if self.reg[reg_a] == self.reg[reg_b]:
                equal = True
                greaterThan = False
                lessThan = False
            elif self.reg[reg_a] > self.reg[reg_b]:
                equal = False
                greaterThan = True
                lessThan = False
            else:
                equal = False
                greaterThan = False
                lessThan = True
            self.fl[5:] = [lessThan, greaterThan, equal]
        else:
            raise Exception("Unsupported ALU operation")


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def HLT(self):
        self.running = False

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.load()
        while self.running:
            ir = self.ram[self.pc]
            reg_a = self.ram[self.pc + 1]
            reg_b = self.ram[self.pc + 2]
            
            if ir == HLT:
                self.running = False
                self.pc += 1
            elif ir == LDI:
                self.reg[reg_a] = reg_b
                self.pc += 3
            elif ir == PRN:
                print(self.reg[reg_a])
                self.pc += 2
            elif ir == MUL:
                ans = self.reg[reg_a] * self.reg[reg_b]
                print(ans)
                self.pc += 3
            elif ir == ADD:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('ADD', reg_a, reg_b)
                self.pc += 3
            elif ir == PUSH:
                self.reg[7] -= 1
                reg_push = self.ram[self.pc + 1]
                val_push = self.reg[reg_push]
                SP = self.reg[7]
                self.ram[SP] = val_push
                self.pc += 2
            elif ir == POP:
                SP = self.reg[7]
                val_pop = self.ram[SP]
                reg_pop = self.ram[self.pc + 1]
                self.reg[reg_pop] = val_pop
                self.reg[7] += 1
                self.pc += 2
            elif ir == CALL:
                self.reg[7] -= 1
                SP = self.reg[7]
                addr_next_instruction = self.pc + 2
                self.ram[SP] = addr_next_instruction
                reg_call = self.ram[self.pc + 1]
                addr_to_go = self.reg[reg_call]
                self.pc = addr_to_go
            elif ir == RET:
                SP = self.reg[7]
                addr_pop = self.ram[SP]
                self.pc = addr_pop
                self.reg[7] += 1
            elif ir == CMP:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('CMP', reg_a, reg_b)
                self.pc += 3
            elif ir == JEQ:
                regJump = self.ram[self.pc + 1]
                addrJump = self.reg[regJump]
                if self.fl[7] is True:
                    self.pc = addrJump
                else:
                    self.pc += 2
            elif ir == JMP:
                regJump = self.ram[self.pc + 1]
                addrJump = self.reg[regJump]
                self.pc = addrJump
            elif ir == JNE:
                regJump = self.ram[self.pc + 1]
                addrJump = self.reg[regJump]
                if self.fl[7] is False:
                    self.pc = addrJump
                else:
                    self.pc += 2
            else:
                print(f'{ir} is not recognized')
                self.pc += 1
