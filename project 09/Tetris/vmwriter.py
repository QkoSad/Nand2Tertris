class VMWriter:
    def __init__(self, vm_path):
        self.my_vm = open(vm_path, "w+")
        self.label_index = 0

    def write_push(self, segment, index):
        self.my_vm.write(f'push {segment} {index}\n')
        #print(f'push {segment} {index}')

    def write_lable(self, label):
        self.my_vm.write(f'label L{label}\n')
        #print(f'label L{label}')

    def write_arithmetic(self, command):
        if command == '+':
            self.my_vm.write('add\n')
            #print('add')
        elif command == '-':
            self.my_vm.write('sub\n')
            #print('sub')
        elif command == 'neg':
            self.my_vm.write('neg\n')
            #print('neg')
        elif command == '=':
            self.my_vm.write('eq\n')
            #print('eq')
        elif command == '>':
            self.my_vm.write('gt\n')
            #print('gt')
        elif command == '<':
            self.my_vm.write('lt\n')
            #print('lt')
        elif command == '&':
            self.my_vm.write('and\n')
            #print('and')
        elif command == '|':
            self.my_vm.write('or\n')
            #print('or')
        elif command == '~':
            self.my_vm.write('not\n')
            #print('not')
        elif command == '*':
            self.write_call('Math.multiply', 2)
        elif command == '/':
            self.write_call('Math.divide', 2)

    def write_pop(self, segment, index):
        #print(f'pop {segment} {index}')
        self.my_vm.write(f'pop {segment} {index}\n')

    def write_goto(self, label):
        self.my_vm.write(f'goto L{label}\n')
        #print(f'goto L{label}')

    def write_if(self, label):
        self.write_arithmetic('~')
        self.my_vm.write(f'if-goto L{label}\n')
        #print(f'if-goto L{label}')

    def write_call(self, label, num_args):
        self.my_vm.write(f'call {label} {num_args}\n')
        #print(f'call {label} {num_args}')

    def write_function(self, label, num_locals):
        self.my_vm.write(f'function {label} {num_locals}\n')
        #print(f'function {label} {num_locals}')

    def write_return(self, func_type):
        if func_type == 'void':
            self.write_push('constant', '0')
        self.my_vm.write('return\n')
        #print(f'return')

    def close_vm_file(self):
        self.my_vm.close()
