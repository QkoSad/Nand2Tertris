import re


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

    def token_type(self, token=None):
        if token is None:
            token = self.token
        if token is None or token == '':
            return None
        if token in self.key_word:
            return 'keyword'
        elif token[0] == '"':
            return 'stringConstant'
        elif re.match(r"\d+", token):
            return 'integerConstant'
        elif token in self.symbols:
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
            i = 0
            # TODO this should be a regex
            while i < len(txt):
                if txt[i] == '/' and txt[i + 1] == '*' and txt[i + 2] == '*':
                    start = i
                    while txt[i] != '*' or txt[i + 1] != '/':  # TODO this is the strange thing in reddit
                        i += 1
                    stop = i + 2
                    txt = txt[:start] + txt[stop:len(txt)]
                    i = start - 1
                i += 1
        self.file = txt
