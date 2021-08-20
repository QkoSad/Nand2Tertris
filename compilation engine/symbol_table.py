class Symbol:
    def __init__(self):
        self.s_name = ''
        self.s_kind = ''
        self.s_type = ''
        self.s_index = 0


class SymbolTable:
    def __init__(self):
        self.sym = []

    def define(self, s_name, s_type, s_kind):
        self.sym.append(Symbol())
        self.sym[-1].s_name = s_name
        self.sym[-1].s_type = s_type
        self.sym[-1].s_kind = s_kind
        self.sym[-1].s_index = self.var_count(s_kind) - 1

    def start_subroutine(self, s_name, s_type):
        self.sym.append(Symbol())
        self.sym[-1].s_name = s_name
        self.sym[-1].s_type = s_type
        self.sym[-1].s_kind = 'argument'
        self.sym[-1].s_index = 0

    def var_count(self, s_kind):
        count = 0  # it is -1 so the first index is 0
        for i in self.sym:
            if i.s_kind == s_kind:
                count += 1
        return count

    def kind_of(self, s_name):
        for i in self.sym:
            if i.s_name == s_name:
                if i.s_kind == 'var':
                    return 'local'
                elif i.s_kind == 'field':
                    return 'this'
                else:
                    return i.s_kind
        return None

    def type_of(self, s_name):
        for i in self.sym:
            if i.s_name == s_name:
                return i.s_type
        return None

    def index_of(self, s_name):
        for i in self.sym:
            if i.s_name == s_name:
                return i.s_index
        return None
