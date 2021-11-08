import re
import os
from pathlib import Path


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
                    # self.token = self.file[i]
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
            txt = re.sub(r"/[*][*][\w*\W*]*[*]/", "", txt)
        self.file = txt


class CompilationEngine:
    def __init__(self):
        self.string = ''
        self.tab = 0

    def write_token(self, tokenizer):
        if tokenizer.token_type() == 'stringConstant':
            self.string += ' ' * self.tab + '<' + tokenizer.token_type() + '> ' + tokenizer.token.strip('"') + ' </' \
                           + tokenizer.token_type() + '>\n'
        else:
            self.string += ' ' * self.tab + '<' + tokenizer.token_type() + '> ' + tokenizer.token + ' </' \
                           + tokenizer.token_type() + '>\n'

    def compile_class(self, tokenizer):
        tokenizer.advance()
        self.string += '<class>\n' + ' ' * self.tab
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        while tokenizer.token != '}':
            if tokenizer.token in ['static', 'field']:
                self.compile_class_var_dec(tokenizer)
            if tokenizer.token in ['constructor', 'function', 'method']:
                self.compile_subroutine(tokenizer)

        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</class>\n'

    def compile_class_var_dec(self, tokenizer):
        self.string += ' ' * self.tab + '<classVarDec>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        while tokenizer.token == ',':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.write_token(tokenizer)
            tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</classVarDec>\n'

    def compile_subroutine(self, tokenizer):
        self.string += ' ' * self.tab + '<subroutineDec>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.compile_parameter_list(tokenizer)
        self.string += ' ' * self.tab + '<subroutineBody>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        while tokenizer.token != '}':
            if tokenizer.token == 'var':
                self.compile_var_dec(tokenizer)
            elif tokenizer.token in ['let', 'if', 'while', 'do', 'return']:
                self.compile_statements(tokenizer)
        self.write_token(tokenizer)
        self.tab -= 2
        self.string += ' ' * self.tab + '</subroutineBody>\n'
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</subroutineDec>\n'

    def compile_parameter_list(self, tokenizer):
        self.string += ' ' * self.tab + '<parameterList>\n'
        self.tab += 2
        while tokenizer.token != ')':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.write_token(tokenizer)
            tokenizer.advance()
            while tokenizer.token == ',':
                self.write_token(tokenizer)
                tokenizer.advance()
                self.write_token(tokenizer)
                tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</parameterList>\n'
        self.write_token(tokenizer)
        tokenizer.advance()

    def compile_var_dec(self, tokenizer):
        self.string += ' ' * self.tab + '<varDec>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        while tokenizer.token == ',':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.write_token(tokenizer)
            tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</varDec>\n'

    def compile_statements(self, tokenizer):
        self.string += ' ' * self.tab + '<statements>\n'
        self.tab += 2
        while True:
            if tokenizer.token == 'let':
                self.compile_let(tokenizer)
            elif tokenizer.token == 'if':
                self.compile_if(tokenizer)
            elif tokenizer.token == 'while':
                self.compile_while(tokenizer)
            elif tokenizer.token == 'do':
                self.compile_do(tokenizer)
            elif tokenizer.token == 'return':
                self.compile_return(tokenizer)
            else:
                self.tab -= 2
                self.string += ' ' * self.tab + '</statements>\n'
                break

    def compile_do(self, tokenizer):
        self.string += ' ' * self.tab + '<doStatement>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        if tokenizer.token == '(':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_expression_list(tokenizer)
            self.write_token(tokenizer)
            tokenizer.advance()
        elif tokenizer.token == '.':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.write_token(tokenizer)
            tokenizer.advance()
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_expression_list(tokenizer)
            self.write_token(tokenizer)
            tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</doStatement>\n'

    def compile_let(self, tokenizer):
        self.string += ' ' * self.tab + '<letStatement>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        if tokenizer.token == '[':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_expression(tokenizer)
            self.write_token(tokenizer)
            tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.compile_expression(tokenizer)
        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</letStatement>\n'

    def compile_while(self, tokenizer):
        self.string += ' ' * self.tab + '<whileStatement>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.compile_expression(tokenizer)
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.compile_statements(tokenizer)
        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</whileStatement>\n'

    def compile_return(self, tokenizer):
        self.string += ' ' * self.tab + '<returnStatement>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        if tokenizer.token != ';':
            self.compile_expression(tokenizer)
        self.write_token(tokenizer)
        tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</returnStatement>\n'

    def compile_if(self, tokenizer):
        self.string += ' ' * self.tab + '<ifStatement>\n'
        self.tab += 2
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.compile_expression(tokenizer)
        self.write_token(tokenizer)
        tokenizer.advance()
        self.write_token(tokenizer)
        tokenizer.advance()
        self.compile_statements(tokenizer)
        self.write_token(tokenizer)
        tokenizer.advance()
        while tokenizer.token == 'else':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_statements(tokenizer)
            self.write_token(tokenizer)
            tokenizer.advance()
        self.tab -= 2
        self.string += ' ' * self.tab + '</ifStatement>\n'

    def compile_expression(self, tokenizer):
        if tokenizer.token in ['(', '~', '-'] or tokenizer.token_type() != 'symbol':
            self.string += ' ' * self.tab + '<expression>\n'
            self.tab += 2
            self.compile_term(tokenizer)
            while tokenizer.token in ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']:
                self.write_token(tokenizer)
                tokenizer.advance()
                self.compile_term(tokenizer)
            self.tab -= 2
            self.string += ' ' * self.tab + '</expression>\n'

    def compile_term(self, tokenizer):
        if tokenizer.token == '(':
            self.string += ' ' * self.tab + '<term>\n'
            self.tab += 2
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_expression(tokenizer)
            self.write_token(tokenizer)
            tokenizer.advance()
            self.tab -= 2
            self.string += ' ' * self.tab + '</term>\n'
        elif tokenizer.token in ['~', '-']:
            self.string += ' ' * self.tab + '<term>\n'
            self.tab += 2
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_term(tokenizer)
            self.tab -= 2
            self.string += ' ' * self.tab + '</term>\n'
        elif tokenizer.token_type() != 'symbol':
            self.string += ' ' * self.tab + '<term>\n'
            self.tab += 2
            self.write_token(tokenizer)
            tokenizer.advance()
            if tokenizer.token == '[':
                self.write_token(tokenizer)
                tokenizer.advance()
                self.compile_expression(tokenizer)
                self.write_token(tokenizer)
                tokenizer.advance()
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'
            elif tokenizer.token == '(':
                self.write_token(tokenizer)
                tokenizer.advance()
                self.compile_expression_list(tokenizer)
                self.write_token(tokenizer)
                tokenizer.advance()
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'
            elif tokenizer.token == '.':
                self.write_token(tokenizer)
                tokenizer.advance()
                self.write_token(tokenizer)
                tokenizer.advance()
                self.write_token(tokenizer)
                tokenizer.advance()
                self.compile_expression_list(tokenizer)
                self.write_token(tokenizer)
                tokenizer.advance()
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'
            else:
                self.tab -= 2
                self.string += ' ' * self.tab + '</term>\n'

    def compile_expression_list(self, tokenizer):
        self.string += ' ' * self.tab + '<expressionList>\n'
        self.tab += 2
        self.compile_expression(tokenizer)
        while tokenizer.token == ',':
            self.write_token(tokenizer)
            tokenizer.advance()
            self.compile_expression(tokenizer)
        self.tab -= 2
        self.string += ' ' * self.tab + '</expressionList>\n'


path = os.getcwd()
for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
        if name[-4:] == 'jack':
            tok = Tokenizer()
            tok.clear_file(Path(root, name))
            ce = CompilationEngine()
            ce.compile_class(tok)
            with open(Path(root, name[:-4] + 'xml'), "w+") as my_xml:
                my_xml.write(ce.string)
