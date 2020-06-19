"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] *  256
        self.pc = 0
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.SP = self.reg[7]
        self.flag = 0b00000000

        self.branch_table = {
                1: self.ldi,
                2: self.prn, 
                3: self.multi,
                4: self.stop,
                5: self.errors,
                6: self.push,
                7: self.pop,
                8: self.call,
                9: self.ret,
                10: self.add,
                11: self.cmp,
                12: self.jmp,
                13: self.jeq,
                14: self.jne
    }
    def load(self):
        """Load a program into memory."""

        # address = 0

        file_name = sys.argv[1]

        # program = [
            # From print8.ls8
            # 0b10000010, # LDI R0,8
            # 0b00000000,
            # 0b00001000,
            # 0b01000111, # PRN R0
            # 0b00000000,
            # 0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        address = 0
        with open(file_name) as f:
            for line in f:
                line = line.rstrip('\n')
                line = line.split('#')[0]
                
                if line:
                    value = int(line, 2)
                    self.ram[address] = value
                    address += 1

        


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MULTIPLY':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = self.flag & 0b11111000
                self.flag = self.flag | 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = self.flag & 0b11111000
                self.flag = self.flag | 0b00000100
            else:
                self.flag = self.flag & 0b11111000
                self.flag = self.flag | 0b00000010
            
        else:
            raise Exception("Unsupported ALU operation")

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

# 10000010 # LDI R0,8
# 00000000
# 00001000
# 10000010 # LDI R1,9
# 00000001
# 00001001
# 10100010 # MUL R0,R1
# 00000000
# 00000001
# 01000111 # PRN R0
# 00000000
# 00000001 # HLT
    """
    PUSH
    decrement SP
    get the value in memory referenced  by pc 
    get the register value at the location in register
    load the value in the register to the memory at the address
    referenced by SP
    increment PC by 2

    POP
    get the value in memeroy referenced by pc
    get the register referenced by the value in memory
    save the value at memory at SP into the register
    increment the SP
    increment PC by 2
    return the alue at the regist   
 


    """
    def ldi(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value
        self.pc += 3

    def prn(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])
        self.pc += 2

    def multi(self):
        reg_num = self.ram_read(self.pc + 1)
        reg_num2 = self.ram_read(self.pc + 2)
        self.alu('MULTIPLY', reg_num, reg_num2)
        self.pc += 3
    def add(self):
        reg_num = self.ram_read(self.pc + 1)
        reg_num2 = self.ram_read(self.pc + 2)
        self.alu('ADD', reg_num, reg_num2)
        self.pc += 3

    def cmp(self):
        reg_num = self.ram_read(self.pc + 1)
        reg_num2 = self.ram_read(self.pc + 2)
        self.alu('CMP', reg_num, reg_num2)
        self.pc += 3

    def stop(self):
        running = False
        return running

    def errors(self):
        print(f'Unknown instruction at address {self.pc}')
        sys.exit(1)

    def push(self):
        self.SP -= 1
        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num] 
        self.ram_write(self.SP, value)
        self.pc += 2

    def pop(self):
        reg_num = self.ram_read(self.pc + 1)
        self.reg[reg_num]= self.ram_read(self.SP)
        self.SP += 1
        self.pc += 2
        return self.reg[reg_num]

    """
    call
    decrement sp
    save the return address in the stack

    get a value in memory at pc for register number
    get the value in register referenced by the value in memory
    set the pc to the value

    return
    read the return address stored in stack
    set the pc to the return address
    increment SP

    """
    def call(self):
        self.SP -= 1
        return_add = self.pc + 2
        self.ram_write(self.SP, return_add)
        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num]
        self.pc = value

    def ret(self):
        return_add = self.ram_read(self.SP)
        self.pc = return_add
        self.SP += 1
    
    def jmp(self):
        reg_num = self.ram_read(self.pc + 1)
        # print('reg_num', reg_num)
        # self.trace()

        jmp_add = self.reg[reg_num]
        # print('jum_add', jmp_add)
        # self.trace()
        self.pc = jmp_add

    def jeq(self):
        flag = self.flag & 0b00000001
        # print('flag1', flag)
        if flag == 1:
            self.jmp()
        else:
            self.pc += 2

    """
     JNE
    JNE register

    If E flag is clear (false, 0), jump to the address stored in the given register.

    Machine code:

    01010110 00000rrr
    56 0r
    """

    def jne(self):
        flag = self.flag & 0b00000001
        # print('flag2', flag)
        if flag == 0:
            self.jmp()
        else:
            self.pc += 2

    def call_table(self, n):

        self.branch_table[n]()


    def run(self):
        """Run the CPU."""
        running = True
  
        while running:
            ir = self.ram_read(self.pc)
            if ir == 0b10000010: # read from memory and setting it to register at cpu
                # reg_num = self.ram_read(self.pc + 1)
                # value = self.ram_read(self.pc + 2)
                # self.reg[reg_num] = value
                # self.pc += 3
                # self.trace()
                self.call_table(1)
                

            elif ir == 0b01000111:  # print
                # reg_num = self.ram_read(self.pc + 1)
                # print(self.reg[reg_num])
                # self.pc += 2
                self.call_table(2)
            elif ir == 0b10100010:   # muliply
                # reg_num = self.ram_read(self.pc + 1)
                # reg_num2 = self.ram_read(self.pc + 2)
                # self.reg[reg_num] *= self.reg[reg_num2]
                # self.pc += 3
                self.call_table(3)

            elif ir ==  0b00000001: # stop running
                # running = False
                # self.pc += 1   
                running  = self.call_table(4)
            elif ir == 0b01000101: # stack push
                self.call_table(6)

            elif ir == 0b01000110: # stack pop
                self.call_table(7)
            elif ir == 0b01010000:  # call subroutine
                self.call_table(8) 
            elif ir == 0b00010001:
                self.call_table(9) # return subroutine
            elif ir == 0b10100000:  # ADD
                self.call_table(10)
            elif ir == 0b10100111: # compare
                self.call_table(11)
            elif ir == 0b01010100:
                self.call_table(12)
            elif ir == 0b01010101:
                self.call_table(13)
            elif ir == 0b01010110:
                self.call_table(14)
            

            else:
                # print(f'Unknown instruction {ir} at address {self.pc}')
                # sys.exit(1)
                # print('ir', bin(ir))
                # self.trace()
                self.call_table(5)
                

