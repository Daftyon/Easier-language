from utils.constants import BOOLEAN, PLUS, SHOW, TRUE, FALSE
from system.builtin_functions.main import is_system_function
from utils.data_classes import *
from utils.errors import SemanticError, ErrorCode
from compiler.symbol_table import SymbolTable


class SemanticAnalyzer(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.symbol_table = SymbolTable()

    def error(self, error_code, message):
        raise SemanticError(
            error_code=error_code,
            message=f'{error_code.value} -> {message}',
        )

    def visit_BinOp(self, node: BinOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: UnaryOp):
        expr = node.expr
        self.visit(expr)
        self.visit(expr)

    @staticmethod
    def visit_Num(node: Num):
        pass

    @staticmethod
    def visit_Str(node: Str):
        pass

    def visit_StrOp(self, node: StrOp):
        self.visit(node.left)
        if node.add.type is not PLUS:
            self.error(ErrorCode.SEMANTIC_ERROR, "only '+' sign can be used for strings' concatenation")
        self.visit(node.right)

    def visit_Compound(self, node: Compound):
        for sub_node in node.get_children():
            self.visit(sub_node)

    def visit_Assign(self, node: Assign):
        var_name = node.left.value
        self.visit(node.right)

        if self.symbol_table.is_defined(var_name):
            return None
        else:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, message=f"value {var_name} is not defined")

    def visit_Var(self, node: Var):
        var_name = node.value
        if self.symbol_table.is_defined(var_name) is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, message=f"value {var_name} is not defined")

    def visit_NoOp(self, node):
        pass

    def visit_Program(self, node: Program):
        nested_symbol_table = SymbolTable(enclosed_parent=None)
        self.symbol_table = nested_symbol_table

        self.visit(node.block)

        self.symbol_table = self.symbol_table.enclosed_parent

    def visit_Block(self, node: Block):
        for declaration in node.var_decs:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecs(self, node: VarDecs):
        declarations = node.get_declarations()
        symbol_type = node.get_type()
        val = node.get_value()
        # print(symbol_type)
        for var in declarations:
            symbol = VarSymbol(var.value, val, symbol_type.value)
            self.symbol_table.define(symbol)

    def visit_VarSymbol(self, node: VarSymbol):
        self.symbol_table.define(node)

    def visit_FunctionDecl(self, node: FunctionDecl):
        """
        function declaration creates a new scope
        """
        nested_scope = SymbolTable(enclosed_parent=self.symbol_table)
        self.symbol_table = nested_scope
        params = node.params
        for param in params:
            self.visit(param)

        block = node.block
        self.visit(block)

        """
        when we leave the function, the scope is finished as well 
        """
        self.symbol_table = self.symbol_table.enclosed_parent

        self.symbol_table.define(node)
    def visit_ShowStatement(self, node: ShowStatement):
        self.visit(node.expression)
    def visit_WhileLoop(self, node: WhileLoop):
        self.visit(node.condition)
        self.visit(node.body)
    def visit_DoWhileLoop(self, node: DoWhileLoop):
        self.visit(node.body)
        self.visit(node.condition)
    def visit_FunctionCall(self, node: FunctionCall):
        if node.name == SHOW:
            if len(node.actual_params) != 1:
                self.error(ErrorCode.NUMBER_OF_ARGUMENTS_MISMATCH_ERROR,
                           "SHOW function expects exactly 1 argument")
            self.visit(node.actual_params[0])
        elif self.symbol_table.is_defined(node.name):
            function: FunctionDecl = self.symbol_table.lookup(node.name)
            parameter_names = function.params
            parameter_values = node.actual_params
            if len(parameter_names) != len(parameter_values):
                self.error(ErrorCode.NUMBER_OF_ARGUMENTS_MISMATCH_ERROR,
                           "Number of arguments passed does not match "
                           "with the function arguments count")
        elif is_system_function(node.name):
            pass
        else:
            self.error(ErrorCode.ID_NOT_FOUND, "function {} is not defined".format(node.name))

    def visit_BooleanSymbol(self, node: BooleanSymbol):
        if node.value not in (TRUE, FALSE):
            self.error(ErrorCode.SEMANTIC_ERROR, "BooleanSymbol got value {}".format(node.value))

    def visit_BoolOp(self, node: BoolOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_NotOp(self, node: NotOp):
        self.visit(node.expr)

    def visit_BoolNotEqual(self, node: BoolNotEqual):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolOr(self, node: BoolOr):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolAnd(self, node: BoolAnd):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolGreaterThan(self, node: BoolGreaterThan):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolGreaterThanOrEqual(self, node: BoolGreaterThanOrEqual):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolLessThan(self, node: BoolLessThan):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolLessThanOrEqual(self, node: BoolLessThanOrEqual):
        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolIsEqual(self, node: BoolIsEqual):
        self.visit(node.left)
        self.visit(node.right)

    def visit_IfBlock(self, node: IfBlock):
        self.visit(node.block)
        self.visit(node.expr)

    def visit_IfStat(self, node: IfStat):
        for if_block in node.if_blocks:
            self.visit(if_block)
        if node.else_block is not None:
            self.visit(node.else_block)

    def visit_ForLoop(self, node: ForLoop):
        base = node.base
        var = base.left.value
        self.symbol_table.define(Symbol(var, None))
        self.visit(node.base)
        self.visit(node.bool_expr)
        self.visit(node.then)
        self.visit(node.block)

    def visit_Break(self, node):
        pass

    def visit_NoneType(self, node):
        pass

    def visit_ReturnStat(self, node: ReturnStat):
        pass

    def visit_list(self, node_list):
      for node in node_list:
        self.visit(node)

    def analyze(self):
        return self.visit(self.tree)
