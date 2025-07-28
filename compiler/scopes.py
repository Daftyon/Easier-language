from compiler.symbol_table import SymbolTable


class NestedScopeable:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def define_new_scope(self):
        nested_scope = SymbolTable(enclosed_parent=self.symbol_table)
        self.symbol_table = nested_scope

    def destroy_current_scope(self):
        self.symbol_table = self.symbol_table.enclosed_parent
