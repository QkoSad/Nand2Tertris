import os
from tokenizer import Tokenizer
from vmwriter import VMWriter
from symbol_table import SymbolTable


# TODO add names to variables when you call for them, aka current_vm_append(thingtobeappended=blablac)

class CompilationEngine:
    def __init__(self, tokenizer, full_path_vm):
        self.string = ''
        self.array_count = self.tab = 0
        self.tokenizer = tokenizer
        self.sym_table = []
        self.class_name = ''
        self.vmwriter = VMWriter(full_path_vm)
        self.current_vm = []  # used to reverse some of the commands, eg a+b need to be a b +
        self.function_type = ''
        self.recursion_index = 0

    def search_sym(self, current_vm):
        if self.sym_table[-1].kind_of(current_vm) is not None:
            return self.sym_table[-1].kind_of(current_vm), self.sym_table[-1].index_of(current_vm)
        for i in range(len(self.sym_table) - 2, -1,
                       -1):  # start from the amount of sym_tables -2 so it starts from one below the current,
            # until it is bigger than -1, walking it backwards
            if self.sym_table[i].kind_of(current_vm) in ('static', 'this'):
                return self.sym_table[i].kind_of(current_vm), self.sym_table[i].index_of(current_vm)

    def write_token(self):
        if self.tokenizer.token_type() == 'stringConstant':
            self.string += ' ' * self.tab + '<' + self.tokenizer.token_type() + '> ' + self.tokenizer.token.strip(
                '"') + ' </' + self.tokenizer.token_type() + '>\n'
        else:
            self.string += ' ' * self.tab + '<' + self.tokenizer.token_type() + '> ' + self.tokenizer.token + ' </' \
                           + self.tokenizer.token_type() + '>\n'

    def compile_class(self):
        self.sym_table.append(SymbolTable())
        self.tokenizer.advance()  # class ->
        self.tokenizer.advance()  # type ->
        self.class_name = self.tokenizer.token
        self.tokenizer.advance()  # name ->
        self.tokenizer.advance()  # { ->
        while self.tokenizer.token != '}':
            if self.tokenizer.token in ['static', 'field']:
                self.compile_class_var_dec()
            if self.tokenizer.token in ['constructor', 'function', 'method']:
                self.compile_subroutine()
        self.tokenizer.advance()
        # self.print_sym_table()
        self.sym_table.pop()
        self.vmwriter.close_vm_file()

    def compile_class_var_dec(self):
        var_kind = tokenizer_main.token
        self.tokenizer.advance()
        var_type = tokenizer_main.token
        self.tokenizer.advance()
        var_name = tokenizer_main.token
        self.sym_table[-1].define(var_name, var_type, var_kind)
        self.tokenizer.advance()
        while self.tokenizer.token == ',':
            self.tokenizer.advance()
            var_name = tokenizer_main.token
            self.sym_table[-1].define(var_name, var_type, var_kind)
            self.tokenizer.advance()
        self.tokenizer.advance()

    def compile_subroutine(self):
        self.sym_table.append(SymbolTable())
        sub_type = self.tokenizer.token
        if sub_type == 'method':
            self.sym_table[-1].start_subroutine('this', self.class_name)
        self.tokenizer.advance()  # subroutine type(function|method|constructor) ->
        self.function_type = self.tokenizer.token
        self.tokenizer.advance()  # subroutine kind(int|void|etc..) ->
        sub_name = self.tokenizer.token
        self.tokenizer.advance()  # subroutine name ->
        self.tokenizer.advance()  # ( ->
        self.compile_parameter_list()
        self.tokenizer.advance()  # { ->
        while self.tokenizer.token == 'var':
            self.compile_var_dec()
        if sub_type == 'constructor':
            self.vmwriter.write_function(f'{self.class_name}.{sub_name}', self.sym_table[-1].var_count('var'))
            self.vmwriter.write_push('constant', str(self.sym_table[-1].var_count('var')))
            self.vmwriter.write_call('Memory.alloc', 1)
            self.vmwriter.write_pop('pointer', 0)
        elif sub_type == 'method':
            self.vmwriter.write_function(f'{self.class_name}.{sub_name}', self.sym_table[-1].var_count('var') + 1)
            self.vmwriter.write_push('argument', 0)
            self.vmwriter.write_push('pointer', 0)
        else:
            self.vmwriter.write_function(f'{self.class_name}.{sub_name}', self.sym_table[-1].var_count('var'))
        while self.tokenizer.token != '}':
            self.compile_statements()
        if sub_type == 'constructor':
            self.vmwriter.write_push('pointer', 0)
        self.tokenizer.advance()
        # self.print_sym_table()
        self.sym_table.pop()

    def compile_parameter_list(self):
        if self.tokenizer.token != ')':
            var_type = self.tokenizer.token
            self.tokenizer.advance()  # var ype ->
            var_name = self.tokenizer.token
            self.sym_table[-1].define(var_name, var_type, 'argument')
            self.tokenizer.advance()  # var name ->
            while self.tokenizer.token == ',':
                self.tokenizer.advance()  # , ->
                var_type = self.tokenizer.token
                self.tokenizer.advance()  # type ->
                var_name = self.tokenizer.token
                self.sym_table[-1].define(var_name, var_type, 'argument')
                self.tokenizer.advance()  # name ->
        self.tokenizer.advance()  # )->

    def compile_var_dec(self):
        var_kind = tokenizer_main.token
        self.tokenizer.advance()
        var_type = tokenizer_main.token
        self.tokenizer.advance()
        var_name = tokenizer_main.token
        self.sym_table[-1].define(var_name, var_type, var_kind)
        self.tokenizer.advance()
        while self.tokenizer.token == ',':
            self.tokenizer.advance()
            var_name = tokenizer_main.token
            self.sym_table[-1].define(var_name, var_type, var_kind)
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
        self.tokenizer.advance()  # do ->
        fname = self.tokenizer.token
        self.tokenizer.advance()  # name ->
        if self.tokenizer.token == '(':
            self.tokenizer.advance()  # ( ->
            count = self.compile_expression_list()
            self.tokenizer.advance()  # ) ->
            self.vmwriter.write_call(f'{self.class_name}.{fname}', count)
        elif self.tokenizer.token == '.':
            self.tokenizer.advance()  # . ->
            fname = f'{fname}.{self.tokenizer.token}'
            self.tokenizer.advance()  # name ->
            self.tokenizer.advance()  # ( ->
            count = self.compile_expression_list()
            self.tokenizer.advance()  # ) ->
            self.vmwriter.write_call(f'{fname}', count)
        self.vmwriter.write_pop('temp', '0')
        self.tokenizer.advance()  # ; ->

    def compile_let(self):
        self.tokenizer.advance()  # let ->
        self.current_vm.append(self.tokenizer.token)
        self.tokenizer.advance()  # var_name ->
        if self.tokenizer.token == '[':
            self.tokenizer.advance()  # [ ->
            self.compile_expression()
            self.tokenizer.advance()  # ] ->
        self.tokenizer.advance()  # = ->
        self.compile_expression()
        self.tokenizer.advance()  # ; ->
        self.vmwriter.write_pop(*self.search_sym(self.current_vm[-1]))
        self.current_vm.pop()

    def compile_while(self):
        self.tokenizer.advance()  # while ->
        label1 = self.vmwriter.label_index
        self.vmwriter.write_lable(self.vmwriter.label_index)
        self.vmwriter.label_index += 1
        self.tokenizer.advance()  # ( ->
        self.compile_expression()
        self.tokenizer.advance()  # ) ->
        label2 = self.vmwriter.label_index
        self.vmwriter.write_if(self.vmwriter.label_index)
        self.tokenizer.advance()  # { ->
        self.compile_statements()
        self.tokenizer.advance()  # } ->
        self.vmwriter.write_goto(label1)
        self.vmwriter.write_lable(label2)
        self.vmwriter.label_index += 1

    def compile_return(self):
        self.tokenizer.advance()  # retrun ->
        if self.tokenizer.token != ';':
            self.compile_expression()
        self.vmwriter.write_return(self.function_type)
        self.tokenizer.advance()  # ; ->

    def compile_if(self):
        self.tokenizer.advance()  # if ->
        self.tokenizer.advance()  # ( ->
        self.compile_expression()
        self.tokenizer.advance()  # ) ->
        label1 = self.vmwriter.label_index
        self.vmwriter.write_if(self.vmwriter.label_index)
        self.vmwriter.label_index += 1
        self.tokenizer.advance()  # { ->
        self.compile_statements()
        self.tokenizer.advance()  # } ->
        label2 = self.vmwriter.label_index
        self.vmwriter.write_goto(self.vmwriter.label_index)
        self.vmwriter.write_lable(label1)
        if self.tokenizer.token == 'else':
            self.tokenizer.advance()  # else ->
            self.tokenizer.advance()  # { ->
            self.compile_statements()
            self.tokenizer.advance()  # } ->
        self.vmwriter.write_lable(label2)
        self.vmwriter.label_index += 1

    def compile_expression(self):
        self.compile_term()
        while self.tokenizer.token in ['+', '-', '*', '/', '|', '=', '>', '<', '&']:
            self.current_vm.append(self.tokenizer.token)
            self.tokenizer.advance()  # symbol ->
            self.compile_term()
            self.vmwriter.write_arithmetic(self.current_vm[-1])
            self.current_vm.pop()
        if self.array_count == 2:
            self.vmwriter.write_pop('pointer', 1)
            self.vmwriter.write_push('that', 0)
            self.vmwriter.write_pop('temp', 0)
            self.vmwriter.write_pop('pointer', 1)
            self.vmwriter.write_push('temp', 0)
            self.vmwriter.write_pop('that', 0)
        elif self.array_count == 1:
            self.vmwriter.write_pop('that', 0)
        self.array_count = 0

    def compile_term(self):
        if self.tokenizer.token == '(':  # expression ()
            self.tokenizer.advance()  # ( ->
            self.compile_expression()
            self.tokenizer.advance()  # ) ->
        elif self.tokenizer.token in ['~', '-']:  # uniry op
            self.current_vm.append(self.tokenizer.token)
            tmp = 'neg' if self.tokenizer.token == '-' else self.tokenizer.token
            self.tokenizer.advance()  # ~ or - ->
            self.compile_term()
            self.vmwriter.write_arithmetic(tmp)
            self.current_vm.pop()
        elif self.tokenizer.token_type() != 'symbol':
            self.current_vm.append(self.tokenizer.token)
            self.tokenizer.advance()  # integer,string,keyword,varnname,subroutine_name,class_name,var_name ->
            if self.tokenizer.token == '[':  # Array
                self.tokenizer.advance()  # [ ->
                self.vmwriter.write_push(*self.search_sym(self.current_vm[-1]))
                self.compile_expression()
                self.vmwriter.write_push(*self.search_sym(self.current_vm[-1]))
                self.vmwriter.write_arithmetic('+')
                self.vmwriter.write_push('pointer', 1)
                self.tokenizer.advance()  # ] ->
                self.array_count += 1
            elif self.tokenizer.token == '(':  # subroutine_name ()
                self.tokenizer.advance()  # ( ->
                count = self.compile_expression_list()
                self.tokenizer.advance()  # ) ->
                self.vmwriter.write_call(f'{self.class_name}.{self.current_vm[-1]}', count)
                self.current_vm.pop()
            elif self.tokenizer.token == '.':  # method
                self.tokenizer.advance()  # . ->
                fname = self.tokenizer.token
                self.tokenizer.advance()  # subroutine name ->
                self.tokenizer.advance()  # ( ->
                count = self.compile_expression_list()
                self.tokenizer.advance()  # ) ->
                self.vmwriter.write_call(f'{self.current_vm[-1]}.{fname}', count)
                self.current_vm.pop()
            elif self.tokenizer.token_type(self.current_vm[-1]) == 'stringConstant':
                for index, item in enumerate(self.current_vm[-1]):
                    self.vmwriter.write_push('constant', ord(item))
                    self.vmwriter.write_call('String.appendChar', 1)
                # TODO  String constants are created using the OS constructor String.new(length)
                #  String assignments like x="cc...c" are handled using a series of calls to the
                #  OS routine String.appendChar(nextChar).
            elif self.tokenizer.token_type(self.current_vm[-1]) == 'integerConstant':
                self.vmwriter.write_push('constant', self.current_vm[-1])
                self.current_vm.pop()
            elif self.tokenizer.token_type(self.current_vm[-1]) == 'identifier':
                self.vmwriter.write_push(*self.search_sym(self.current_vm[-1]))
                self.current_vm.pop()
            elif self.current_vm[-1] == 'true':
                self.vmwriter.write_push('constant', '1')
                self.vmwriter.write_arithmetic('neg')
                self.current_vm.pop()
            elif self.current_vm[-1] == 'false' or self.current_vm[-1] == 'null':
                self.vmwriter.write_push('constant', '0')
                self.current_vm.pop()

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

    def print_sym_table(self):
        print('------------------------------------------')
        for i in range(len(self.sym_table[-1].sym)):
            print(f'{self.sym_table[-1].sym[i].s_kind} '
                  f'{self.sym_table[-1].sym[i].s_type} '
                  f'{self.sym_table[-1].sym[i].s_name} '
                  f'{self.sym_table[-1].sym[i].s_index}')


if __name__ == '__main__':
    path = 'C:/Users/AGrudev/Desktop/nand2tetris/projects/11/test'
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name[-4:] == 'jack':
                tokenizer_main = Tokenizer()
                tokenizer_main.clear_file(path + '/' + name)
                print(name + '\n\n')
                full_path = path + '/' + name[:-4] + 'vm'
                comp_eng_main = CompilationEngine(tokenizer_main, full_path)
                comp_eng_main.compile_class()
