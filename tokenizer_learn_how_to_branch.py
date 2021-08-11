import re
import os


class Tokenizer:

    def __init__(self):
        self.i = 0
        self.file = ''
        self.symbols = ('(', ')', '[', ']', '}', '{', '>', '<', '=', '*', '+', '-', '/', '.', ';', ',', '&', '|',
                        '~')
        self.key_word = (
            'class', 'method', 'function', 'constructor', 'int', 'boolean', 'char', 'void', 'var', 'static', 'field',
            'let', 'do', 'if', 'else', 'while', 'return', 'true', 'false', 'null', 'this')
        self.token = ''

    def token_type(self):
        if self.token is None or self.token == '':
            return None
        if self.token in self.key_word:
            return 'keyword'
        elif self.token[0] == '"':
            return 'stringConstant'
        elif re.match(r"\d+", self.token):
            return 'integerConstant'
        elif self.token in self.symbols:
            return 'symbol'
        else:
            return 'identifier'

    def advance(self):
        token = ''
        i = self.i
        while i < len(self.file):
            if re.match(r'\s', self.file[i]):
                i = i + 1
                continue
            else:
                if self.file[i] in self.symbols:
                    self.token = self.file[i]
                    self.i = i + 1
                    return
                elif self.file[i] == '"':
                    i += 1
                    while self.file[i] != '"':
                        token += self.file[i]
                        i += 1
                    self.i = i + 1
                    self.token = '"' + token + '"'
                    return
                else:
                    while re.match(r'\w', self.file[i]):
                        token += self.file[i]
                        if i + 1 > len(self.file) - 1:
                            break
                        i += 1
                    self.i = i
                    self.token = token
                    return

    def clear_file(self, directory):
        with open(directory, "r") as my_file:
            txt = my_file.read()
            txt = re.sub(r"//.*", "", txt)
            txt = re.sub(r"/[*][*].*[*]/", "", txt)
            txt = re.sub(r"/[*][*][\w\W]*[*]/", "", txt)
        self.file = txt


def token_type(t):
    if t is None or t == '':
        return None
    if t in ('(', ')', '[', ']', '}', '{', '>', '<', '=', '*', '+', '-', '/', '.', ';', ',', '&', '|',
             '~'):
        return 'keyword'
    elif t[0] == '"':
        return 'stringConstant'
    elif re.match(r"\d+", t):
        return 'integerConstant'
    elif t in ('(', ')', '[', ']', '}', '{', '>', '<', '=', '*', '+', '-', '/', '.', ';', ',', '&', '|',
               '~'):
        return 'symbol'
    else:
        return 'identifier'


class CompilationEngine:
    def __init__(self, tokenizer, full_path1):
        self.string = ''
        self.tab = 0
        self.tokenizer = tokenizer
        self.sub_table = []
        self.sub_table_index = -1
        self.class_name = ''
        self.vmwriter = VMWriter(full_path1)
        self.tmp = []

    def write_token(self):
        if self.tokenizer.token_type() == 'stringConstant':
            self.string += ' ' * self.tab + '<' + self.tokenizer.token_type() + '> ' + self.tokenizer.token.strip(
                '"') + ' </' + self.tokenizer.token_type() + '>\n'
        else:
            self.string += ' ' * self.tab + '<' + self.tokenizer.token_type() + '> ' + self.tokenizer.token + ' </' \
                           + self.tokenizer.token_type() + '>\n'

    def compile_class(self):
        self.sub_table.append(SymbolTable())
        self.sub_table_index += 1
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.class_name = self.tokenizer.token
        self.tokenizer.advance()
        self.tokenizer.advance()
        while self.tokenizer.token != '}':
            if self.tokenizer.token in ['static', 'field']:
                self.compile_class_var_dec()
            if self.tokenizer.token in ['constructor', 'function', 'method']:
                self.compile_subroutine()
        self.tokenizer.advance()
        # self.print_sub_table()

    def compile_class_var_dec(self):
        var_kind = tokenizer_main.token
        self.tokenizer.advance()
        var_type = tokenizer_main.token
        self.tokenizer.advance()
        var_name = tokenizer_main.token
        self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
        self.tokenizer.advance()
        while self.tokenizer.token == ',':
            self.tokenizer.advance()
            var_name = tokenizer_main.token
            self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
            self.tokenizer.advance()
        self.tokenizer.advance()

    def compile_subroutine(self):
        self.sub_table.append(SymbolTable())
        self.sub_table_index += 1
        if self.tokenizer.token == 'method':
            self.sub_table[self.sub_table_index].start_subroutine('this', self.class_name)
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.compile_parameter_list()
        self.tokenizer.advance()
        while self.tokenizer.token != '}':
            if self.tokenizer.token == 'var':
                self.compile_var_dec()
            elif self.tokenizer.token in ['let', 'if', 'while', 'do', 'return']:
                self.compile_statements()
        self.tokenizer.advance()
        # self.print_sub_table()
        self.sub_table.pop(self.sub_table_index)
        self.sub_table_index -= 1

    def compile_parameter_list(self):
        if self.tokenizer.token != ')':
            var_type = self.tokenizer.token
            self.tokenizer.advance()
            var_name = self.tokenizer.token
            self.sub_table[self.sub_table_index].define(var_name, var_type, 'argument')
            self.tokenizer.advance()
            while self.tokenizer.token == ',':
                self.tokenizer.advance()
                var_type = self.tokenizer.token
                self.tokenizer.advance()
                var_name = self.tokenizer.token
                self.sub_table[self.sub_table_index].define(var_name, var_type, 'argument')
                self.tokenizer.advance()
        self.tokenizer.advance()

    def compile_var_dec(self):
        var_kind = tokenizer_main.token
        self.tokenizer.advance()
        var_type = tokenizer_main.token
        self.tokenizer.advance()
        var_name = tokenizer_main.token
        self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
        self.tokenizer.advance()
        while self.tokenizer.token == ',':
            self.tokenizer.advance()
            var_name = tokenizer_main.token
            self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
            self.tokenizer.advance()
        self.tokenizer.advance()

    def compile_statements(self):
        while True:
            if self.tokenizer.token == 'let':
                self.compile_let()
            elif self.tokenizer.token == 'if':
                self.compile_if()
            elif self.tokenizer.token == 'while':
                self.compile_while()
            elif self.tokenizer.token == 'do':
                self.compile_do()
            elif self.tokenizer.token == 'return':
                self.compile_return()
            else:
                break

    def compile_do(self):
        self.tokenizer.advance()
        self.tokenizer.advance()
        if self.tokenizer.token == '(':
            self.tokenizer.advance()
            self.compile_expression_list()
            self.tokenizer.advance()
        elif self.tokenizer.token == '.':
            self.tokenizer.advance()
            self.tokenizer.advance()
            self.tokenizer.advance()
            self.compile_expression_list()
            self.tokenizer.advance()
        self.tokenizer.advance()

    def compile_let(self):
        self.tokenizer.advance()  # let ->
        self.tmp.append(self.tokenizer.token)
        self.tokenizer.advance()  # var_name ->
        # TODO can add validation not a fan since this is the only validation
        if self.tokenizer.token == '[':
            self.tokenizer.advance()  # [ ->
            self.compile_expression()
            self.tokenizer.advance()  # ] ->
        self.tokenizer.advance()  # = ->
        self.compile_expression()
        self.tokenizer.advance()  # ; ->
        self.vmwriter.write_pop(self.sub_table[self.sub_table_index].kind_of(self.tmp[-1]),
                                self.sub_table[self.sub_table_index].index_of(self.tmp[-1]))
        self.tmp.pop()

    def compile_while(self):
        self.tokenizer.advance()  # while ->
        self.vmwriter.write_lable(self.vmwriter.label_index)
        self.vmwriter.label_index += 1
        self.tokenizer.advance()  # ( ->
        self.compile_expression()
        self.tokenizer.advance()  # ) ->
        self.vmwriter.write_arithmetic('~')
        self.vmwriter.write_goto(self.vmwriter.label_index)
        self.vmwriter.label_index -= 1
        self.tokenizer.advance()  # { ->
        self.compile_statements()
        self.tokenizer.advance()  # } ->
        self.vmwriter.write_goto(self.vmwriter.label_index)
        self.vmwriter.label_index -= 1
        self.vmwriter.write_lable(self.vmwriter.label_index)
        self.vmwriter.label_index += 1

    def compile_return(self):
        self.tokenizer.advance()
        if self.tokenizer.token != ';':
            self.compile_expression()
        self.tokenizer.advance()

    def compile_if(self):
        self.tokenizer.advance()  # if ->
        self.tokenizer.advance()  # ( ->
        self.compile_expression()
        self.vmwriter.write_if(self.vmwriter.label_index)
        self.vmwriter.label_index += 1
        self.tokenizer.advance()  # ) ->
        self.tokenizer.advance()  # { ->
        self.compile_statements()
        self.tokenizer.advance()  # } ->
        self.vmwriter.write_goto(self.vmwriter.label_index)
        self.vmwriter.label_index -= 1
        self.vmwriter.write_lable(self.vmwriter.label_index)
        self.vmwriter.label_index += 1
        while self.tokenizer.token == 'else':
            self.tokenizer.advance()  # else ->
            self.tokenizer.advance()  # { ->
            self.compile_statements()
            self.tokenizer.advance()  # } ->
        self.vmwriter.write_lable(self.vmwriter.label_index)
        self.vmwriter.label_index += 1

    def compile_expression(self):
        self.compile_term()
        while self.tokenizer.token in ['+', '-', '*', '/', '|', '=', '>', '<']:
            self.tmp.append(self.tokenizer.token)
            self.tokenizer.advance()  # symbol ->
            self.compile_term()
            self.vmwriter.write_arithmetic(self.tmp[-1])
            self.tmp.pop()

    def compile_term(self):
        if self.tokenizer.token == '(':  # expression ()
            self.tokenizer.advance()  # ( ->
            self.compile_expression()
            self.tokenizer.advance()  # ) ->
        elif self.tokenizer.token in ['~', '-']:  # uniry op
            self.tmp.append(self.tokenizer.token)
            self.tokenizer.advance()  # ~ or - ->
            self.compile_term()
            self.vmwriter.write_arithmetic(self.tmp[-1])
            self.tmp.pop()
        elif self.tokenizer.token_type() != 'symbol':
            self.tmp.append(self.tokenizer.token)
            self.tokenizer.advance()  # integer,string,keyword,varnname,subroutine_name,class_name,var_name ->
            if self.tokenizer.token == '[':  # varname []
                self.tokenizer.advance()  # [ ->
                self.compile_expression()
                self.tokenizer.advance()  # ] ->
            elif self.tokenizer.token == '(':  # subroutine_name ()
                self.tokenizer.advance()  # ( ->
                c = self.compile_expression_list()
                self.tokenizer.advance()  # ) ->
                self.vmwriter.write_call(self.tmp[-1], c)
                self.tmp.pop()
            # methods later
            #     elif self.tokenizer.token == '.':  # class anem, var name .
            #         self.tokenizer.advance()  # . ->
            #         self.tokenizer.advance()  # subroutine name ->
            #         self.tokenizer.advance()  # ( ->
            #         self.compile_expression_list()
            #         self.tokenizer.advance()  # ) ->
            elif token_type(self.tmp[-1]) == 'integerConstant':
                self.vmwriter.write_push('constant', self.tmp[-1])
                self.tmp.pop()
            elif token_type(self.tmp[-1]) == 'identifier':
                self.vmwriter.write_push(self.sub_table[self.sub_table_index].kind_of(self.tmp[-1]),
                                         self.sub_table[self.sub_table_index].index_of(self.tmp[-1]))
                self.tmp.pop()
                # TODO currently checking only the first table need to check all probably a function 
                #  that checks all and returns index

    def compile_expression_list(self):
        count_exp = 0
        if self.tokenizer.token in ['(', '~', '-'] or self.tokenizer.token_type() != 'symbol':
            count_exp += 1
            self.compile_expression()
            while self.tokenizer.token == ',':
                count_exp += 1
                self.tokenizer.advance()  # ,
                self.compile_expression()
        return count_exp

    def print_sub_table(self):
        for i in range(self.sub_table[self.sub_table_index].index):
            print(f'{self.sub_table[self.sub_table_index].sym[i].s_kind} '
                  f'{self.sub_table[self.sub_table_index].sym[i].s_type} '
                  f'{self.sub_table[self.sub_table_index].sym[i].s_name} '
                  f'{self.sub_table[self.sub_table_index].sym[i].s_index}')
        print('------------------------------------------')


class Symbol:
    def __init__(self):
        self.s_name = ''
        self.s_kind = ''
        self.s_type = ''
        self.s_index = 0


class SymbolTable:
    def __init__(self):
        self.index = 0
        self.sym = []

    def define(self, s_name, s_type, s_kind):
        self.sym.append(Symbol())
        self.sym[self.index].s_name = s_name
        self.sym[self.index].s_type = s_type
        self.sym[self.index].s_kind = s_kind
        self.sym[self.index].s_index = self.var_count(s_kind)
        self.index += 1

    def start_subroutine(self, s_name, s_type):
        self.sym.append(Symbol())
        self.sym[self.index].s_name = s_name
        self.sym[self.index].s_type = s_type
        self.sym[self.index].s_kind = 'argument'
        self.sym[self.index].s_index = 0
        self.index += 1

    def var_count(self, s_kind):
        count = -1
        for i in self.sym:
            if i.s_kind == s_kind:
                count += 1
        return count

    def kind_of(self, s_name):
        for i in self.sym:
            if i.s_name == s_name:
                if i.s_kind == 'var':
                    return 'local'
                else:
                    return i.s_kind

    def type_of(self, s_name):
        for i in self.sym:
            if i.s_name == s_name:
                return i.s_type

    def index_of(self, s_name):
        for i in self.sym:
            if i.s_name == s_name:
                return i.s_index


class VMWriter:
    def __init__(self, vm_path):
        self.my_vm = open(vm_path, "w+")
        self.label_index = 0

    def write_push(self, segment, index):
        self.my_vm.write(f'push {segment} {index}')
        print(f'push {segment} {index}')

    def write_lable(self, label):
        self.my_vm.write(f'label L{label}')
        print(f'label L{label}')

    def write_arithmetic(self, command):
        if command == '+':
            self.my_vm.write('add')
            print('add')
        elif command == '-':
            self.my_vm.write('sub')
            print('sub')
        elif command == '-':
            self.my_vm.write('neg')
            print('neg')
        elif command == '=':
            self.my_vm.write('eq')
            print('eq')
        elif command == '>':
            self.my_vm.write('gt')
            print('gt')
        elif command == '<':
            self.my_vm.write('lt')
            print('lt')
        elif command == '&':
            self.my_vm.write('and')
            print('and')
        elif command == '|':
            self.my_vm.write('or')
            print('or')
        elif command == '~':
            self.my_vm.write('not')
            print('not')
        elif command == '*':
            self.my_vm.write('mult')
            print('mult')
        elif command == '/':
            self.my_vm.write('div')
            print('div')

    def write_pop(self, segment, index):
        print(f'pop {segment} {index}')
        self.my_vm.write(f'pop {segment} {index}')

    def write_goto(self, label):
        self.my_vm.write(f'goto L{label}')
        print(f'goto L{label}')

    def write_if(self, label):
        self.write_arithmetic('~')
        self.my_vm.write(f'if-goto L{label}')
        print(f'if-goto L{label}')

    def write_call(self, label, num_args):
        self.my_vm.write(f'call {label} {num_args}')
        print(f'call {label} {num_args}')

    def write_function(self, label, num_locals):
        self.my_vm.write(f'function {label} {num_locals}')
        print(f'function {label} {num_locals}')

    def write_return(self):
        self.my_vm.write('return')
        print(f'return')

    def close_vm_file(self):
        self.my_vm.close()


path = 'C:/Users/SQA-AGrudev/Desktop/nand2tetris/projects/11/test'
for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
        if name[-4:] == 'jack':
            tokenizer_main = Tokenizer()
            tokenizer_main.clear_file(path + '/' + name)
            print(name)
            full_path = path + '/' + name[:-4] + 'xml'
            comp_eng_main = CompilationEngine(tokenizer_main, full_path)
            comp_eng_main.compile_class()
