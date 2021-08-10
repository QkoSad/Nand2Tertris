import re
import os


class Tokenizer:

    def __init__(self):
        self.i = 0
        self.file = ''
        self.symbols = ('(', ')', '[', ']', '}', '{', '>', '<', '=', '*', '+', '-', '/', '.', ';', ',', '&', '|',
                        '~', '&gt;', '&lt;', '&amp;')
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
                    if self.file[i] == '>':
                        self.token = '&gt;'
                    elif self.file[i] == '<':
                        self.token = '&lt;'
                    elif self.file[i] == '&':
                        self.token = '&amp;'
                    else:
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


class CompilationEngine:
    def __init__(self, tokenizer):
        self.string = ''
        self.tab = 0
        self.tokenizer = tokenizer
        self.sub_table = []
        self.sub_table_index = -1
        self.class_name = ''

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
        self.string += '<class>\n' + ' ' * self.tab
        self.tab += 2
        self.write_token()
        self.tokenizer.advance()
        self.class_name = self.tokenizer.token
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        while self.tokenizer.token != '}':
            if self.tokenizer.token in ['static', 'field']:
                self.compile_class_var_dec()
            if self.tokenizer.token in ['constructor', 'function', 'method']:
                self.compile_subroutine()
        self.write_token()
        self.tokenizer.advance()
        self.print_sub_table()
        self.tab -= 2
        self.string += ' ' * self.tab + '</class>\n'

    def compile_class_var_dec(self):
        self.string += ' ' * self.tab + '<classVarDec>\n'
        self.tab += 2
        var_kind = tokenizer_main.token
        self.write_token()
        self.tokenizer.advance()
        var_type = tokenizer_main.token
        self.write_token()
        self.tokenizer.advance()
        var_name = tokenizer_main.token
        self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
        self.write_token()
        self.tokenizer.advance()
        while self.tokenizer.token == ',':
            self.write_token()
            self.tokenizer.advance()
            var_name = tokenizer_main.token
            self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
            self.write_token()
            self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</classVarDec>\n'

    def compile_subroutine(self):
        self.sub_table.append(SymbolTable())
        self.sub_table_index += 1
        if self.tokenizer.token == 'method':
            self.sub_table[self.sub_table_index].start_subroutine('this', self.class_name)
        self.string += ' ' * self.tab + '<subroutineDec>\n'
        self.tab += 2
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.compile_parameter_list()
        self.string += ' ' * self.tab + '<subroutineBody>\n'
        self.tab += 2
        self.write_token()
        self.tokenizer.advance()
        while self.tokenizer.token != '}':
            if self.tokenizer.token == 'var':
                self.compile_var_dec()
            elif self.tokenizer.token in ['let', 'if', 'while', 'do', 'return']:
                self.compile_statements()
        self.write_token()
        self.tab -= 2
        self.string += ' ' * self.tab + '</subroutineBody>\n'
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</subroutineDec>\n'
        self.print_sub_table()
        self.sub_table.pop(self.sub_table_index)
        self.sub_table_index -= 1

    def print_sub_table(self):
        for i in range(self.sub_table[self.sub_table_index].index):
            print(f'{self.sub_table[self.sub_table_index].sym[i].s_kind} '
                  f'{self.sub_table[self.sub_table_index].sym[i].s_type} '
                  f'{self.sub_table[self.sub_table_index].sym[i].s_name} '
                  f'{self.sub_table[self.sub_table_index].sym[i].s_index}')
        print('------------------------------------------')

    def compile_parameter_list(self):
        self.string += ' ' * self.tab + '<parameterList>\n'
        self.tab += 2
        if self.tokenizer.token != ')':
            var_type = self.tokenizer.token
            self.write_token()  # var type
            self.tokenizer.advance()
            var_name = self.tokenizer.token
            self.sub_table[self.sub_table_index].define(var_name, var_type, 'argument')
            self.write_token()  # var name
            self.tokenizer.advance()
            while self.tokenizer.token == ',':
                self.write_token()  # ,
                self.tokenizer.advance()
                var_type = self.tokenizer.token
                self.write_token()  # var type
                self.tokenizer.advance()
                var_name = self.tokenizer.token
                self.sub_table[self.sub_table_index].define(var_name, var_type, 'argument')
                self.write_token()  # var name
                self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</parameterList>\n'
        self.write_token()  # )
        self.tokenizer.advance()

    def compile_var_dec(self):
        self.string += ' ' * self.tab + '<varDec>\n'
        self.tab += 2
        var_kind = tokenizer_main.token
        self.write_token()
        self.tokenizer.advance()
        var_type = tokenizer_main.token
        self.write_token()
        self.tokenizer.advance()
        var_name = tokenizer_main.token
        self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
        self.write_token()
        self.tokenizer.advance()
        while self.tokenizer.token == ',':
            self.write_token()
            self.tokenizer.advance()
            var_name = tokenizer_main.token
            self.sub_table[self.sub_table_index].define(var_name, var_type, var_kind)
            self.write_token()
            self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</varDec>\n'

    def compile_statements(self):
        self.string += ' ' * self.tab + '<statements>\n'
        self.tab += 2
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
                self.tab -= 2
                self.string += ' ' * self.tab + '</statements>\n'
                break

    def compile_do(self):
        self.string += ' ' * self.tab + '<doStatement>\n'
        self.tab += 2
        self.write_token()  # do
        self.tokenizer.advance()
        self.write_token()  # subroutine name | class name | var name
        self.tokenizer.advance()
        if self.tokenizer.token == '(':
            self.write_token()  # (
            self.tokenizer.advance()
            self.compile_expression_list()
            self.write_token()  # )
            self.tokenizer.advance()
        elif self.tokenizer.token == '.':
            self.write_token()  # .
            self.tokenizer.advance()
            self.write_token()  # subroutine name
            self.tokenizer.advance()
            self.write_token()  # (
            self.tokenizer.advance()
            self.compile_expression_list()
            self.write_token()  # )
            self.tokenizer.advance()
        self.write_token()  # ;
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</doStatement>\n'

    def compile_let(self):
        self.string += ' ' * self.tab + '<letStatement>\n'
        self.tab += 2
        self.write_token()  # let
        self.tokenizer.advance()
        self.write_token()  # var name
        self.tokenizer.advance()
        # if not self.check_if_exist():
        #     raise
        # TODO can add validation not a fan since this is the only validation
        if self.tokenizer.token == '[':
            self.write_token()  # [
            self.tokenizer.advance()
            self.compile_expression()
            self.write_token()  # ]
            self.tokenizer.advance()
        self.write_token()  # =
        self.tokenizer.advance()
        self.compile_expression()
        self.write_token()  # ;
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</letStatement>\n'

    def compile_while(self):
        self.string += ' ' * self.tab + '<whileStatement>\n'
        self.tab += 2
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.compile_expression()
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.compile_statements()
        self.write_token()
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</whileStatement>\n'

    def compile_return(self):
        self.string += ' ' * self.tab + '<returnStatement>\n'
        self.tab += 2
        self.write_token()
        self.tokenizer.advance()
        if self.tokenizer.token != ';':
            self.compile_expression()
        self.write_token()
        self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</returnStatement>\n'

    def compile_if(self):
        self.string += ' ' * self.tab + '<ifStatement>\n'
        self.tab += 2
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.compile_expression()
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.compile_statements()
        self.write_token()
        self.tokenizer.advance()
        while self.tokenizer.token == 'else':
            self.write_token()
            self.tokenizer.advance()
            self.write_token()
            self.tokenizer.advance()
            self.compile_statements()
            self.write_token()
            self.tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</ifStatement>\n'

    def compile_expression(self):
        if self.tokenizer.token in ['(', '~', '-'] or self.tokenizer.token_type() != 'symbol':
            self.string += ' ' * self.tab + '<expression>\n'
            self.tab += 2
            self.compile_term()
            while self.tokenizer.token in ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']:
                self.write_token()
                self.tokenizer.advance()
                self.compile_term()
            self.tab -= 2
            self.string += ' ' * self.tab + '</expression>\n'

    def compile_term(self):
        if self.tokenizer.token == '(':
            self.string += ' ' * self.tab + '<term>\n'
            self.tab += 2
            self.write_token()
            self.tokenizer.advance()
            self.compile_expression()
            self.write_token()
            self.tokenizer.advance()
            self.tab -= 2
            self.string += ' ' * self.tab + '</term>\n'
        elif self.tokenizer.token in ['~', '-']:
            self.string += ' ' * self.tab + '<term>\n'
            self.tab += 2
            self.write_token()
            self.tokenizer.advance()
            self.compile_term()
            self.tab -= 2
            self.string += ' ' * self.tab + '</term>\n'
        elif self.tokenizer.token_type() != 'symbol':
            self.string += ' ' * self.tab + '<term>\n'
            self.tab += 2
            self.write_token()
            self.tokenizer.advance()
            if self.tokenizer.token == '[':
                self.write_token()
                self.tokenizer.advance()
                self.compile_expression()
                self.write_token()
                self.tokenizer.advance()
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'
            elif self.tokenizer.token == '(':
                self.write_token()
                self.tokenizer.advance()
                self.compile_expression_list()
                self.write_token()
                self.tokenizer.advance()
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'
            elif self.tokenizer.token == '.':
                self.write_token()
                self.tokenizer.advance()
                self.write_token()
                self.tokenizer.advance()
                self.write_token()
                self.tokenizer.advance()
                self.compile_expression_list()
                self.write_token()
                self.tokenizer.advance()
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'
            else:
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'

    def compile_expression_list(self):
        self.string += ' ' * self.tab + '<expressionList>\n'
        self.tab += 2
        self.compile_expression()
        while self.tokenizer.token == ',':
            self.write_token()
            self.tokenizer.advance()
            self.compile_expression()
        self.tab -= 2
        self.string += ' ' * self.tab + '</expressionList>\n'


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
    def __init__(self):
        pass

    def write_push(self, segment, index):
        txt = f'push {segment} {index}'
        return txt

    def write_pop(self, segment, index):
        txt = f'pop {segment} {index}'
        return txt


path = 'C:/Users/SQA-AGrudev/Desktop/nand2tetris/projects/10/Square'
for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
        if name[-4:] == 'jack':
            tokenizer_main = Tokenizer()
            tokenizer_main.clear_file(path + '/' + name)
            print(name)
            comp_eng_main = CompilationEngine(tokenizer_main)
            comp_eng_main.compile_class()
            with open(path + '/' + name[:-4] + 'xml', "w+") as my_xml:
                my_xml.write(comp_eng_main.string)
