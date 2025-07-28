from utils.constants import *
from utils.data_classes import *


class SymbolTable:
    def __init__(self, enclosed_parent=None):
        self._symbols = {}
        self.enclosed_parent: SymbolTable = enclosed_parent

    def get_symbols(self):
        return self._symbols

    def define(self, symbol: AbstractSymbol):
        self._symbols[symbol.name] = symbol

    def get_var_scope(self, scope, var: str):
        if scope is None:
            raise ValueError("can't find scope for " + var)

        if var in scope.get_symbols():
            return scope

        return self.get_var_scope(self.enclosed_parent, var)

    def assign(self, var: str, value: Symbol):
        if var in self._symbols:
            self._symbols[var] = value
        else:
            scope: SymbolTable = self.get_var_scope(self, var)
            scope.assign(var, value)

    def is_defined(self, var):
        return self.lookup(var) is not None

    def is_valid_type(self, symbol_type):
        return self.is_defined(symbol_type)

    def lookup(self, var):
        cur_var = self._symbols.get(var, None)
        if cur_var is not None:
            return cur_var

        if self.enclosed_parent:
            return self.enclosed_parent.lookup(var)

        return None

    def __str__(self):
        res = ""
        for symbol in self._symbols.values():
            res += str(symbol) + ","
        return f"SymbolTable({res})"
