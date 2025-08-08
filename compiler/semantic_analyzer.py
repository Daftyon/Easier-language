from utils.constants import BOOLEAN, PLUS, SHOW, TRUE, FALSE,REALISTIC
from system.builtin_functions.main import is_system_function
from utils.data_classes import *
from utils.errors import SemanticError, ErrorCode
from compiler.symbol_table import SymbolTable

from utils.colors import ProofConsole, Colors

class SemanticAnalyzer(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.symbol_table = SymbolTable()
        self.theorems = {}  # Dictionary to store theorems by name
        self.proofs = {}
        self.hypotheses = {}  # Track hypotheses
        self.tests = {}  # Track tests
        self.axioms = {}  # Track axioms




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
        """Enhanced to handle realistic values"""
        if node.value not in (TRUE, FALSE, REALISTIC):
            self.error(ErrorCode.SEMANTIC_ERROR, "BooleanSymbol got invalid value {}".format(node.value))
            
    def visit_RealisticSymbol(self, node: RealisticSymbol):
        """Validate realistic symbol"""
        if node.value != REALISTIC:
            self.error(ErrorCode.SEMANTIC_ERROR, "RealisticSymbol must have REALISTIC value")
        
        # Validate probability range
        if hasattr(node, 'probability') and (node.probability < 0.0 or node.probability > 1.0):
            self.error(ErrorCode.SEMANTIC_ERROR, "Realistic probability must be between 0.0 and 1.0")

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
    def visit_SwitchStatement(self, node: SwitchStatement):
            """Semantic analysis for switch statement"""
            # Analyze the switch expression
            self.visit(node.expression)
            
            # Check for duplicate case values
            case_values = []
            default_count = 0
            
            for case_block in node.case_blocks:
                if case_block.is_default:
                    default_count += 1
                    if default_count > 1:
                        self.error(ErrorCode.SEMANTIC_ERROR, 
                                "Multiple default cases in switch statement")
                else:
                    # Visit the case value expression
                    self.visit(case_block.value)
                    
                    # Check for duplicate case values (simplified check)
                    case_values.append(case_block.value)
                
                # Analyze statements in the case block
                self.visit_list(case_block.statements)
    
    def visit_CaseBlock(self, node: CaseBlock):
        """Semantic analysis for individual case blocks"""
        if not node.is_default and node.value is not None:
            self.visit(node.value)
        
        # Analyze all statements in the case block
        for statement in node.statements:
            self.visit(statement)
    def visit_ConstDeclaration(self, node: ConstDeclaration):
        """Semantic analysis for constant declarations"""
        declarations = node.get_declarations()
        symbol_type = node.get_type()
        val = node.get_value()
        
        # Constants must have a value
        if val is None:
            self.error(ErrorCode.SEMANTIC_ERROR, "Constants must be initialized with a value")
        
        # Validate the constant value expression
        self.visit(val)
        
        # Define constant symbols in symbol table
        for var in declarations:
            # Check if already defined
            if self.symbol_table.is_defined(var.value):
                existing_symbol = self.symbol_table.lookup(var.value)
                if isinstance(existing_symbol, ConstSymbol):
                    self.error(ErrorCode.DUPLICATE_ID, f"Constant {var.value} is already defined")
                else:
                    self.error(ErrorCode.DUPLICATE_ID, f"Identifier {var.value} is already defined as variable")
            
            symbol = ConstSymbol(var.value, val, symbol_type.value)
            self.symbol_table.define(symbol)
    
    def visit_Assign(self, node: Assign):
        """Enhanced assignment validation to prevent const modification"""
        var_name = node.left.value
        self.visit(node.right)

        if self.symbol_table.is_defined(var_name):
            symbol = self.symbol_table.lookup(var_name)
            
            # Check if trying to assign to a constant
            if isinstance(symbol, ConstSymbol):
                self.error(ErrorCode.SEMANTIC_ERROR, 
                         f"Cannot assign to constant '{var_name}'. Constants are immutable.")
            
            return None
        else:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, message=f"Variable {var_name} is not defined")
    def visit_TheoremDeclaration(self, node: TheoremDeclaration):
        """Semantic analysis for theorem declarations"""
        theorem_name = node.get_name()
        
        # Check if theorem name is already defined
        if theorem_name in self.theorems:
            ProofConsole.error(f"Theorem '{theorem_name}' is already declared")
            self.error(ErrorCode.DUPLICATE_ID, f"Theorem '{theorem_name}' is already declared")
        
        # Check if theorem name conflicts with variables/functions
        if self.symbol_table.is_defined(theorem_name):
            ProofConsole.error(f"Theorem name '{theorem_name}' conflicts with existing identifier")
            self.error(ErrorCode.DUPLICATE_ID, 
                     f"Theorem name '{theorem_name}' conflicts with existing identifier")
        
        # Analyze the theorem statement
        if node.get_statement() is not None:
            self.visit(node.get_statement())
        
        # Register the theorem
        self.theorems[theorem_name] = node
        
        # Print colored declaration
        print(f"{Colors.BRIGHT_BLUE}{Colors.BOLD}Declared theorem:{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{theorem_name}{Colors.RESET} "
              f"{Colors.YELLOW}(unproven){Colors.RESET}")
        
    def visit_ProofDeclaration(self, node: ProofDeclaration):
        """Semantic analysis for proof declarations"""
        theorem_name = node.get_theorem_name()
        
        # Check if the theorem being proved exists
        if theorem_name not in self.theorems:
            ProofConsole.error(f"Cannot prove theorem '{theorem_name}' - theorem not declared")
            self.error(ErrorCode.ID_NOT_FOUND, 
                     f"Cannot prove theorem '{theorem_name}' - theorem not declared")
        
        # Check if this theorem already has a proof
        if theorem_name in self.proofs:
            ProofConsole.error(f"Theorem '{theorem_name}' already has a proof")
            self.error(ErrorCode.DUPLICATE_ID, 
                     f"Theorem '{theorem_name}' already has a proof")
        
        # Analyze each proof step
        for step in node.get_proof_steps():
            self.visit(step)
        
        # Register the proof
        self.proofs[theorem_name] = node
        
        # Link proof to theorem
        theorem = self.theorems[theorem_name]
        theorem.set_proof(node)
        
        # Basic proof validation (for now, just check if it's complete)
        if node.is_proof_complete():
            print(f"{Colors.SUCCESS}{Colors.BOLD}[✓] Complete proof for theorem:{Colors.RESET} "
                  f"{Colors.BRIGHT_WHITE}{theorem_name}{Colors.RESET}")
            # For now, mark as valid if complete (later add real proof checking)
            node.mark_valid()
            theorem.mark_proven()
        else:
            print(f"{Colors.WARNING}{Colors.BOLD}[!] Incomplete proof for theorem:{Colors.RESET} "
                  f"{Colors.BRIGHT_WHITE}{theorem_name}{Colors.RESET}")
    
    def visit_ProofStep(self, node: ProofStep):
        """Semantic analysis for individual proof steps"""
        # Analyze the statement in the proof step
        if node.get_statement() is not None:
            self.visit(node.get_statement())
    
    def visit_QEDStatement(self, node: QEDStatement):
        """Semantic analysis for QED statements"""
        # QED statements are always valid
        pass
    def visit_HypothesisStatement(self, node: HypothesisStatement):
        """Semantic analysis for hypothesis statements"""
        hypothesis_name = node.get_name()
        
        # Check if hypothesis name conflicts
        if hypothesis_name in self.hypotheses:
            self.error(ErrorCode.DUPLICATE_ID, f"Hypothesis '{hypothesis_name}' is already defined")
        
        # Analyze the hypothesis statement
        if node.get_statement() is not None:
            self.visit(node.get_statement())
        
        # Register hypothesis
        self.hypotheses[hypothesis_name] = node
        
        print(f"{Colors.BRIGHT_CYAN}[HYPOTHESIS]{Colors.RESET} {Colors.BRIGHT_WHITE}{hypothesis_name}{Colors.RESET} assumed")
    def visit_TestStatement(self, node: TestStatement):
        """Semantic analysis for test statements"""
        test_name = node.get_test_name()
        hypothesis_name = node.get_hypothesis_name()
        
        # Check if test name conflicts
        if test_name in self.tests:
            self.error(ErrorCode.DUPLICATE_ID, f"Test '{test_name}' is already defined")
        
        # Check if hypothesis being tested exists
        if hypothesis_name not in self.hypotheses:
            self.error(ErrorCode.ID_NOT_FOUND, 
                     f"Cannot test unknown hypothesis '{hypothesis_name}'")
        
        # Analyze the test condition
        if node.get_test_condition() is not None:
            self.visit(node.get_test_condition())
        
        # Register test
        self.tests[test_name] = node
        
        from utils.colors import Colors
        print(f"{Colors.BRIGHT_YELLOW}[TEST]{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{test_name}{Colors.RESET} "
              f"for hypothesis {Colors.CYAN}{hypothesis_name}{Colors.RESET}")
    def visit_AxiomDeclaration(self, node: AxiomDeclaration):
        """Semantic analysis for axiom declarations"""
        axiom_name = node.get_name()
        
        # Check if axiom name conflicts
        if axiom_name in self.axioms:
            self.error(ErrorCode.DUPLICATE_ID, f"Axiom '{axiom_name}' is already defined")
        
        # Check if axiom name conflicts with other identifiers
        if (axiom_name in self.theorems or 
            self.symbol_table.is_defined(axiom_name)):
            self.error(ErrorCode.DUPLICATE_ID, 
                     f"Axiom name '{axiom_name}' conflicts with existing identifier")
        
        # Analyze the axiom statement
        if node.get_statement() is not None:
            self.visit(node.get_statement())
        
        # Register axiom
        self.axioms[axiom_name] = node
        
        from utils.colors import Colors
        print(f"{Colors.BRIGHT_MAGENTA}[AXIOM]{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{axiom_name}{Colors.RESET} "
              f"{Colors.MAGENTA}(self-evident truth){Colors.RESET}")    
   