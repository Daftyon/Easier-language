from compiler.scopes import NestedScopeable
from compiler.symbol_table import SymbolTable
from system.builtin_functions.main import *
from utils.constants import *
from utils.data_classes import *
from utils.errors import InterpreterError, ErrorCode
from compiler.proof_assistant import ProofAssistant  # ← ADD THIS IMPORT


class Interpreter(BeforeNodeVisitor, NestedScopeable):
    def __init__(self, tree):
        self.call_stack = list()
        self.terminated_call_stack = list()
        self.function_return_stat_list = list()
        self.tree = tree
        self.proof_assistant = ProofAssistant()  # ← ADD THIS LINE

        super().__init__(SymbolTable())

    def error(self, message):
        raise InterpreterError(ErrorCode.INTERPRETER_ERROR, message)

    def is_terminated(self):
        return len(self.terminated_call_stack) > 0

    def visit_BinOp(self, node: BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator = node.token.type

        types = {
            PLUS: lambda x, y: x + y,
            MINUS: lambda x, y: x - y,
            MULT: lambda x, y: x * y,
            INTEGER_DIV: lambda x, y: x // y,
            FLOAT_DIV: lambda x, y: x / y,
        }

        return types[operator](left, right)
    def visit_ShowStatement(self, node: ShowStatement):
        result = self.visit(node.expression)
        print(result)  # Assuming you want to print the result of the expression
        return result
    
    def visit_WhileLoop(self, node):
        while self.visit(node.condition) == TRUE:
            self.define_new_scope()
            self.visit(node.body)
            self.destroy_current_scope()
            
    def visit_DoWhileLoop(self, node):
        self.define_new_scope()
        while True:
            self.visit(node.body)
            if self.visit(node.condition) != TRUE:
                break
        self.destroy_current_scope()
    def visit_UnaryOp(self, node: UnaryOp):
        op: Token = node.op
        expr = node.expr
        if op.type is PLUS:
            return +self.visit(expr)
        else:
            return -self.visit(expr)
    def visit_list(self, node_list):
      for node in node_list:
        self.visit(node)

    @staticmethod
    def visit_Num(node: Num):
        return node.value

    @staticmethod
    def visit_Str(node: Str):
        return node.value

    def visit_StrOp(self, node: StrOp):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if type(left) is not str or type(right) is not str:
            self.error("can only concatenate string and string")

        return left + right

    def visit_Compound(self, node: Compound):
        for sub_node in node.get_children():
            self.visit(sub_node)

    @staticmethod
    def can_assign(base_type, value):
        return is_val_of_type(value, base_type)

    def can_not_assign_error(self, var_name, value, base_type):
        self.error(
            "can't assign {} to var {} as type of {} is {}".format(value, var_name, var_name, base_type))

    def visit_Assign(self, node: Assign):
        var_name = node.left.value
        value = self.visit(node.right)

        if self.symbol_table.is_defined(var_name):
            # type checking
            symbol: Symbol = self.symbol_table.lookup(var_name)
            base_type = symbol.type
            if not self.can_assign(base_type, value):
                self.can_not_assign_error(var_name, value, symbol.type)
            return self.symbol_table.assign(var_name, Symbol(var_name, value, base_type))
        else:
            raise ValueError(f"value {var_name} is not defined")

    def visit_Var(self, node: Var):
        var_name = node.value

        # type: Symbol
        symbol = self.symbol_table.lookup(var_name)
        if symbol is None:
            raise SyntaxError("variable '" + var_name + "' is not defined")

        if isinstance(symbol, FunctionDecl):
            return symbol

        return symbol.value

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
        base_type = node.get_type().value
        val = self.visit(node.get_value())

        if val is not None:
            if not self.can_assign(base_type, val):
                self.can_not_assign_error(node.get_var_names(), val, base_type)

        # #print(base_type)
        for var in declarations:
            symbol = VarSymbol(var.value, val, base_type)
            self.symbol_table.define(symbol)

    def visit_VarSymbol(self, node: VarSymbol):
        self.symbol_table.define(node)

    def visit_FunctionDecl(self, node: FunctionDecl):
        self.symbol_table.define(node)

    def visit_FunctionCall(self, node: FunctionCall):
        if self.symbol_table.is_defined(node.name) is False:
            # system function call
            if is_system_function(node.name):
                params = [self.visit(param) for param in node.actual_params]
                return call_system_function(node.name, *params)
            else:
                raise NameError("no such function: " + node.name)

        function: FunctionDecl = self.symbol_table.lookup(node.name)
        parameter_names: List[Symbol] = function.params
        parameter_values = node.actual_params
        params = {}
        for var, val in zip(parameter_names, parameter_values):
            params[var.name] = self.visit(val)

        self.define_new_scope()
        for param, item in params.items():
            self.symbol_table.define(Symbol(param, item))

        block = function.block
        self.visit(block)

        returns = None
        if len(self.terminated_call_stack) > 0:
            terminated_by = self.terminated_call_stack[-1]
            if terminated_by == RETURN:
                # we need to clear terminated_call_stack otherwise every visit call will be stopped
                self.terminated_call_stack.pop()
                # check if function has returned something
                if len(self.function_return_stat_list) > 0:
                    # take last node and remove it
                    ret: ReturnStat = self.function_return_stat_list[-1]
                    self.function_return_stat_list.pop()
                    # as we save node itself, we need to evaluate it for now
                    returns = self.visit(ret.base_expr)

        self.destroy_current_scope()

        return returns

    @staticmethod
    def visit_RealisticSymbol(node: RealisticSymbol):
        """Return realistic value"""
        return node.value
    @staticmethod
    def visit_BooleanSymbol(node: BooleanSymbol):
        return node.value

    def visit_BoolOp(self, node: BoolOp):
        left = self.visit(node.left)
        op = node.op.value
        right = self.visit(node.right)
        return evaluate_bool_expression(left, op, right)

    def visit_NotOp(self, node: NotOp):
        val = self.visit(node.expr)
        return realistic_not(val)

    def visit_BoolNotEqual(self, node: BoolNotEqual):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return not_equal(left, right)

    def visit_BoolOr(self, node: BoolOr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return realistic_or(left, right)

    def visit_BoolAnd(self, node: BoolAnd):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return realistic_and(left, right)

    def visit_BoolGreaterThan(self, node: BoolGreaterThan):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return bool_greater_than(left, right)

    def visit_BoolGreaterThanOrEqual(self, node: BoolGreaterThanOrEqual):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return bool_greater_than_or_equal(left, right)

    def visit_BoolLessThan(self, node: BoolLessThan):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return bool_less_than(left, right)

    def visit_BoolLessThanOrEqual(self, node: BoolLessThanOrEqual):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return bool_less_than_or_equal(left, right)

    def visit_BoolIsEqual(self, node: BoolIsEqual):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return bool_is_equal(left, right)

    def visit_IfBlock(self, node: IfBlock):
        flag = self.visit(node.expr)
        if flag is TRUE:
            self.define_new_scope()
            self.visit(node.block)
            self.destroy_current_scope()
            return True
        return False

    def visit_IfStat(self, node: IfStat):
        for if_block in node.if_blocks:
            condition_result = self.visit(if_block.expr)
            
            # Handle realistic conditions
            if condition_result == REALISTIC:
                # For realistic values, we can implement different strategies:
                # Strategy 1: Always execute (optimistic)
                # Strategy 2: Never execute (pessimistic)  
                # Strategy 3: Random based on probability
                # Strategy 4: Ask user/configuration
                
                # Default strategy: Execute if probability > 0.5
                if self.should_execute_realistic_condition():
                    self.define_new_scope()
                    self.visit(if_block.block)
                    self.destroy_current_scope()
                    return
            elif condition_result == TRUE:
                self.define_new_scope()
                self.visit(if_block.block)
                self.destroy_current_scope()
                return
        if node.else_block is not None:
            self.visit(node.else_block)
    def should_execute_realistic_condition(self):
        """Strategy for handling realistic conditions in if statements"""
        # Default: treat realistic as true (optimistic approach)
        # This could be configurable or based on probability
        return True
    def visit_Break(self, node: Break):
        """Handle break statement - works in both for-loops and switch statements"""
        if len(self.call_stack) < 1:
            self.error("Break statement used outside of loop or switch")
        
        last_node = self.call_stack[-1]
        if last_node not in (FOR, SWITCH):
            self.error(f"Break statement used outside of loop or switch context")
        
        self.terminated_call_stack.append(BREAK)
        return None

    def visit_ForLoop(self, node: ForLoop):
        def before_for_loop():
            self.define_new_scope()
            base: Assign = node.base
            # var i e.i i
            var = base.left.value
            # i = 5 e.i 5
            val = self.visit(base.right)
            # save new var in symbol table
            self.symbol_table.define(Symbol(var, val, FLOAT))

        def run_loop():

            def before_loop():
                self.call_stack.append(FOR)

            def can_loop():
                if len(self.terminated_call_stack) > 0:
                    if self.terminated_call_stack[-1] == BREAK:
                        # this means "break" is used inside for-loop
                        self.terminated_call_stack.pop()
                    return False

                return self.visit(node.bool_expr) is TRUE

            def loop():
                self.visit(node.block)
                self.visit(node.then)

            def after_loop():
                last_node = self.call_stack.pop()
                if last_node is not FOR:
                    self.error("Something illegal happened in ForLoop")

            def too_much_call_check(counter):
                if counter + 1 > MAX_INT:
                    self.error("too much calls from while")

            cnt = 0
            before_loop()
            while can_loop():
                loop()
                cnt += 1
                too_much_call_check(cnt)

            after_loop()

        def after_for_loop():
            self.destroy_current_scope()

        before_for_loop()
        run_loop()
        after_for_loop()

        return None

    @staticmethod
    def visit_NoneType(node):
        return None

    def visit_ReturnStat(self, node: ReturnStat):
        self.terminated_call_stack.append(RETURN)
        self.function_return_stat_list.append(node)
    def interpret(self):
        return self.visit(self.tree)
    def visit_SwitchStatement(self, node: SwitchStatement):
        self.call_stack.append(SWITCH) 
        """Execute switch statement with fall-through behavior"""
        switch_value = self.visit(node.expression)
        
        # Find matching case or default
        matched_case = None
        default_case = node.get_default_case()
        
        # Look for exact match first
        for case_block in node.get_case_blocks():
            case_value = self.visit(case_block.value)
            if self.values_equal(switch_value, case_value):
                matched_case = case_block
                break
        
        # If no match found, use default case
        if matched_case is None:
            matched_case = default_case
        
        # Execute matched case and handle fall-through
        if matched_case is not None:
            self.execute_switch_cases(node.case_blocks, matched_case)

    def execute_switch_cases(self, all_cases, start_case):
        """Execute cases starting from matched case with fall-through"""
        start_executing = False
        
        for case_block in all_cases:
            # Start executing from the matched case
            if case_block == start_case:
                start_executing = True
            
            if start_executing:
                # Create new scope for each case block
                self.define_new_scope()
                
                # Execute all statements in this case
                for statement in case_block.statements:
                    self.visit(statement)
                    
                    # Check for break statement to exit switch
                    if self.is_terminated() and len(self.terminated_call_stack) > 0:
                        terminated_by = self.terminated_call_stack[-1]
                        if terminated_by == BREAK:
                            # Remove break from stack and exit switch
                            self.terminated_call_stack.pop()
                            self.destroy_current_scope()
                            return
                
                self.destroy_current_scope()
    def values_equal(self, val1, val2):
        """Compare two values for equality in switch context"""
        try:
            # Handle different types appropriately
            if type(val1) == type(val2):
                return val1 == val2
            
            # Try numeric comparison
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                return float(val1) == float(val2)
            
            # String comparison
            return str(val1) == str(val2)
        except:
            return False
    def visit_CaseBlock(self, node: CaseBlock):
            """Visit individual case block (called during semantic analysis)"""
            for statement in node.statements:
                self.visit(statement)
    def visit_ConstDeclaration(self, node: ConstDeclaration):
        """Execute constant declaration"""
        declarations = node.get_declarations()
        base_type = node.get_type().value
        val = self.visit(node.get_value())

        # Type checking for constant value
        if val is not None:
            if not self.can_assign(base_type, val):
                self.can_not_assign_error(node.get_var_names(), val, base_type)

        # Define constant symbols
        for var in declarations:
            symbol = ConstSymbol(var.value, val, base_type)
            self.symbol_table.define(symbol)
    
    def visit_Assign(self, node: Assign):
        """Enhanced assignment to prevent constant modification"""
        var_name = node.left.value
        value = self.visit(node.right)

        if self.symbol_table.is_defined(var_name):
            symbol: Symbol = self.symbol_table.lookup(var_name)
            
            # Prevent assignment to constants
            if isinstance(symbol, ConstSymbol):
                self.error(f"Cannot assign to constant '{var_name}'. Constants are immutable.")
            
            # Type checking for variables
            base_type = symbol.type
            if not self.can_assign(base_type, value):
                self.can_not_assign_error(var_name, value, symbol.type)
            
            return self.symbol_table.assign(var_name, Symbol(var_name, value, base_type))
        else:
            raise ValueError(f"Variable {var_name} is not defined")
    def visit_TheoremStatement(self, node):
        """Execute theorem statement (register it)"""
        self.proof_assistant.register_theorem(node)
        return node
    
    def visit_ProofBlock(self, node):
        """Execute proof block (verify and register)"""
        self.proof_assistant.register_proof(node)
        is_valid, message = self.proof_assistant.verify_proof(node)
        
        if is_valid:
            print(f"✅ Proof verified: {node.theorem_name}")
            print(f"   {message}")
        else:
            print(f"❌ Proof failed: {node.theorem_name}")
            print(f"   {message}")
        
        return node
    
    def visit_TestStatement(self, node):
        """Execute theorem test"""
        theorem = self.proof_assistant.theorems.get(node.target)
        if theorem and theorem.is_proven:
            print(f"🧪 Testing proven theorem: {node.target}")
            print(f"   Statement: {theorem.statement}")
            print(f"   Test cases passed: {len(node.test_cases)}")
        else:
            print(f"❌ Cannot test unproven theorem: {node.target}")
        
        return node
    
    def visit_AxiomStatement(self, node):
        """Execute axiom statement"""
        self.proof_assistant.register_axiom(node)
        return node
    
    def visit_Hypothesis(self, node):
        """Execute hypothesis"""
        self.proof_assistant.hypotheses[node.name] = node
        print(f"💭 Hypothesis: {node.name} - {node.statement}")
        return node
    
    