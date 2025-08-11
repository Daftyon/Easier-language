from compiler.scopes import NestedScopeable
from compiler.symbol_table import SymbolTable
from system.builtin_functions.main import *
from utils.constants import *
from utils.data_classes import *
from utils.errors import InterpreterError, ErrorCode
from utils.colors import ProofConsole, Colors
from system.package_manager import EasierHubPackageManager

from typing import Dict, Any, List, Optional

class Interpreter(BeforeNodeVisitor, NestedScopeable):
    def __init__(self, tree):
        self.call_stack = list()
        self.terminated_call_stack = list()
        self.function_return_stat_list = list()
        self.tree = tree
        self.theorems = {}  # Store theorems during interpretation
        self.proofs = {}    # Store proofs during interpretation
        self.hypotheses = {}  # Store active hypotheses
        self.tests = {}  # Store tests
        self.axioms = {}  # Store axioms
        self.definitions = {}  # Store definitions
        self.brought_packages = {}  # Store imported packages
        self.package_manager = EasierHubPackageManager()
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
    def visit_TheoremDeclaration(self, node: TheoremDeclaration):
        """Execute theorem declaration - register theorem in system"""
        theorem_name = node.get_name()
        
        # Register theorem in interpreter's theorem database
        self.theorems[theorem_name] = node
        
        # Use colored console output
        ProofConsole.theorem_declared(
            theorem_name, 
            node.get_statement(), 
            node.is_theorem_proven()
        )
        
        return node
        
    def visit_ProofDeclaration(self, node: ProofDeclaration):
        """Execute proof declaration - register and validate proof"""
        theorem_name = node.get_theorem_name()
        
        # Check if theorem exists
        if theorem_name not in self.theorems:
            ProofConsole.error(f"Cannot create proof for unknown theorem: {theorem_name}")
            self.error(f"Cannot create proof for unknown theorem: {theorem_name}")
        
        # Register proof
        self.proofs[theorem_name] = node
        
        # Use colored console output for proof start
        ProofConsole.proof_start(theorem_name, len(node.get_proof_steps()))
        
        # Execute proof steps (for now, just display them)
        for i, step in enumerate(node.get_proof_steps(), 1):
            ProofConsole.proof_step(i, step.get_statement())
        
        # Check if proof is complete
        if node.is_proof_complete():
            ProofConsole.proof_complete(theorem_name)
            
            # Link proof to theorem
            theorem = self.theorems[theorem_name]
            theorem.set_proof(node)
            
            # For now, assume complete proofs are valid
            node.mark_valid()
            theorem.mark_proven()
        else:
            ProofConsole.proof_incomplete(theorem_name)
        
        return node
    
    def visit_ProofStep(self, node: ProofStep):
        """Execute individual proof step"""
        # For now, just evaluate the statement
        if node.get_statement() is not None:
            result = self.visit(node.get_statement())
            return result
        return None
    
    def visit_QEDStatement(self, node: QEDStatement):
        """Execute QED statement"""
        # QED marks end of proof
        return "QED"
    
    def visit_HypothesisStatement(self, node: HypothesisStatement):
        """Execute hypothesis statement - add assumption to context"""
        hypothesis_name = node.get_name()
        
        # Register hypothesis
        self.hypotheses[hypothesis_name] = node
        
        # Print colored hypothesis
        from utils.colors import Colors
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}[HYPOTHESIS]{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{hypothesis_name}{Colors.RESET}: "
              f"{Colors.CYAN}{node.get_statement()}{Colors.RESET} "
              f"{Colors.YELLOW}(assumed){Colors.RESET}")
        
        return node
    
    def visit_ProofDeclaration(self, node: ProofDeclaration):
        """Enhanced proof execution with hypothesis support"""
        theorem_name = node.get_theorem_name()
        
        if theorem_name not in self.theorems:
            self.error(f"Cannot create proof for unknown theorem: {theorem_name}")
        
        self.proofs[theorem_name] = node
        
        from utils.colors import ProofConsole, Colors
        ProofConsole.proof_start(theorem_name, len(node.get_proof_steps()))
        
        # Execute proof steps with hypothesis support
        for i, step in enumerate(node.get_proof_steps(), 1):
            if step.is_hypothesis_step():
                # Display hypothesis step
                print(f"   {Colors.BRIGHT_CYAN}{i}. [HYPOTHESIS]{Colors.RESET} "
                      f"{Colors.BRIGHT_WHITE}{step.get_hypothesis_name()}{Colors.RESET}: "
                      f"{Colors.CYAN}{step.get_statement()}{Colors.RESET}")
            else:
                # Regular proof step
                ProofConsole.proof_step(i, step.get_statement())
        
        if node.is_proof_complete():
            ProofConsole.proof_complete(theorem_name)
            
            theorem = self.theorems[theorem_name]
            theorem.set_proof(node)
            node.mark_valid()
            theorem.mark_proven()
        else:
            from utils.colors import ProofConsole
            ProofConsole.proof_incomplete(theorem_name)
        
        return node
    def visit_TestStatement(self, node: TestStatement):
        """Execute test statement - test hypothesis against condition"""
        test_name = node.get_test_name()
        hypothesis_name = node.get_hypothesis_name()
        
        # Get the hypothesis being tested
        if hypothesis_name not in self.hypotheses:
            self.error(f"Cannot test unknown hypothesis: {hypothesis_name}")
        
        hypothesis = self.hypotheses[hypothesis_name]
        test_condition = node.get_test_condition()
        
        # Evaluate both hypothesis and test condition
        hypothesis_value = self.visit(hypothesis.get_statement())
        test_condition_value = self.visit(test_condition)
        
        # Determine test result
        test_result = self.evaluate_test(hypothesis_value, test_condition_value)
        node.set_test_result(test_result)
        
        # Store test
        self.tests[test_name] = node
        
        # Print colored test result
        from utils.colors import Colors
        result_color = Colors.SUCCESS if test_result == "PASS" else \
                      Colors.ERROR if test_result == "FAIL" else Colors.WARNING
        
        print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}[TEST]{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{test_name}{Colors.RESET}: "
              f"{result_color}{test_result}{Colors.RESET}")
        print(f"   Hypothesis '{hypothesis_name}': {hypothesis_value}")
        print(f"   Test condition: {test_condition_value}")
        
        return node
    
    def evaluate_test(self, hypothesis_value, test_condition_value):
        """Evaluate test result based on hypothesis and test condition values"""
        from utils.constants import TRUE, FALSE, REALISTIC
        
        # Simple test logic: does hypothesis match test condition?
        if hypothesis_value == test_condition_value:
            return "PASS"
        elif (hypothesis_value == REALISTIC or test_condition_value == REALISTIC):
            return "UNCERTAIN"  # Realistic values create uncertainty
        else:
            return "FAIL"
    
    def visit_ProofDeclaration(self, node: ProofDeclaration):
        """Enhanced proof execution with test support"""
        theorem_name = node.get_theorem_name()
        
        if theorem_name not in self.theorems:
            self.error(f"Cannot create proof for unknown theorem: {theorem_name}")
        
        self.proofs[theorem_name] = node
        
        from utils.colors import ProofConsole, Colors
        ProofConsole.proof_start(theorem_name, len(node.get_proof_steps()))
        
        # Execute proof steps with hypothesis and test support
        for i, step in enumerate(node.get_proof_steps(), 1):
            if step.is_hypothesis_step():
                # Display hypothesis step
                print(f"   {Colors.BRIGHT_CYAN}{i}. [HYPOTHESIS]{Colors.RESET} "
                      f"{Colors.BRIGHT_WHITE}{step.get_hypothesis_name()}{Colors.RESET}: "
                      f"{Colors.CYAN}{step.get_statement()}{Colors.RESET}")
                      
            elif step.is_test_step():
                # Display test step
                print(f"   {Colors.BRIGHT_YELLOW}{i}. [TEST]{Colors.RESET} "
                      f"{Colors.BRIGHT_WHITE}{step.get_test_name()}{Colors.RESET}: "
                      f"{Colors.YELLOW}{step.get_statement()}{Colors.RESET}")
            else:
                # Regular proof step
                ProofConsole.proof_step(i, step.get_statement())
        
        if node.is_proof_complete():
            ProofConsole.proof_complete(theorem_name)
            
            theorem = self.theorems[theorem_name]
            theorem.set_proof(node)
            node.mark_valid()
            theorem.mark_proven()
        else:
            ProofConsole.proof_incomplete(theorem_name)
        
        return node
    def visit_AxiomDeclaration(self, node: AxiomDeclaration):
            """Execute axiom declaration - register fundamental truth"""
            axiom_name = node.get_name()
            
            # Register axiom
            self.axioms[axiom_name] = node
            
            # Print colored axiom
            from utils.colors import Colors
            print(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}[AXIOM]{Colors.RESET} "
                f"{Colors.BRIGHT_WHITE}{axiom_name}{Colors.RESET}")
            print(f"   Statement: {Colors.MAGENTA}{node.get_statement()}{Colors.RESET}")
            print(f"   Status: {Colors.SUCCESS}{Colors.BOLD}SELF-EVIDENT{Colors.RESET} "
                f"{Colors.MAGENTA}(requires no proof){Colors.RESET}")
            
            return node
     
    def visit_DefinitionDeclaration(self, node: DefinitionDeclaration):
        """Execute definition declaration - register definition"""
        definition_name = node.get_name()
        
        # Register definition
        self.definitions[definition_name] = node
        
        # Print colored definition
        from utils.colors import Colors
        params_str = f"({', '.join(node.get_parameters())})" if node.has_parameters() else ""
        
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}[DEFINITION]{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{definition_name}{params_str}{Colors.RESET}")
        print(f"   Body: {Colors.CYAN}{node.get_body()}{Colors.RESET}")
        
        if node.has_parameters():
            print(f"   Parameters: {Colors.YELLOW}{', '.join(node.get_parameters())}{Colors.RESET}")
        
        print(f"   Status: {Colors.SUCCESS}DEFINED{Colors.RESET}")
        
        return node
    
    def lookup_definition(self, name):
        """Look up a definition by name"""
        return self.definitions.get(name, None)
    
    def apply_definition(self, definition_name, arguments=None):
        """Apply a definition with given arguments"""
        definition = self.lookup_definition(definition_name)
        if not definition:
            return None
        
        # For now, just return the definition body
        # In a more advanced system, we'd substitute parameters with arguments
        definition.increment_usage()
        return definition.get_body()
    def visit_BringStatement(self, node: BringStatement):
        """Execute bring statement - import package from Easier Hub"""
        package_name = node.get_package_name()
        
        # Check if already loaded
        if package_name in self.brought_packages:
            print(f"Package '{package_name}' already loaded")
            return node

        # Fetch package from Easier Hub
        from utils.colors import  Colors
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}[BRING]{Colors.RESET} "
              f"Fetching package '{Colors.BRIGHT_WHITE}{package_name}{Colors.RESET}' "
              f"from {Colors.CYAN}{node.get_source_hub()}{Colors.RESET}...")
        
        package_data = self.package_manager.fetch_package(package_name)
        
        if package_data is None:
            self.error(f"Failed to load package '{package_name}'")
            return node
        
        # Store package content
        node.set_package_content(package_data)
        self.brought_packages[package_name] = node
        
        # Process package content
        self.process_package_content(node, package_data)
        
        # Success message
        version = package_data.get('version', 'unknown')
        cached = " (cached)" if package_data.get('cached') else ""
        
        print(f"{Colors.SUCCESS}[SUCCESS]{Colors.RESET} "
              f"Package '{Colors.BRIGHT_WHITE}{package_name}{Colors.RESET}' "
              f"v{version} loaded{cached}")
        
        # Show available items if specific import
        if node.get_specific_items():
            available_items = self.get_package_items(package_data)
            for item in node.get_specific_items():
                if item in available_items:
                    print(f"  ✓ {Colors.GREEN}{item}{Colors.RESET}")
                else:
                    print(f"  ✗ {Colors.ERROR}{item} (not found){Colors.RESET}")
        
        return node
    
    def process_package_content(self, bring_node: BringStatement, package_data: Dict[str, Any]):
        """Process imported package content"""
        content = package_data.get('content', {})
        alias = bring_node.get_alias()
        specific_items = bring_node.get_specific_items()
        
        # Create package namespace in symbol table
        package_symbols = {}
        
        # Process different types of content
        for key, value in content.items():
            if key.startswith('schema:'):
                # Handle schema definitions
                schema_name = key.split(':', 1)[1]
                package_symbols[schema_name] = value
            
            elif hasattr(value, 'items'):  # BringObject
                # Handle object definitions (functions, constants, etc.)
                if specific_items:
                    # Only import specific items
                    for item in specific_items:
                        if item in value.items:
                            self.symbol_table.define(Symbol(item, value.items[item]))
                else:
                    # Import all items under package namespace
                    package_symbols.update(value.items)
            
            else:
                # Handle primitive values
                if specific_items:
                    if key in specific_items:
                        self.symbol_table.define(Symbol(key, value))
                else:
                    package_symbols[key] = value
        
        # Define package namespace if not specific import
        if not specific_items and package_symbols:
            self.symbol_table.define(Symbol(alias, package_symbols))
    
    def get_package_items(self, package_data: Dict[str, Any]) -> list:
        """Get list of available items in package"""
        items = []
        content = package_data.get('content', {})
        
        for key, value in content.items():
            if key.startswith('schema:'):
                items.append(key.split(':', 1)[1])
            elif hasattr(value, 'items'):
                items.extend(value.items.keys())
            else:
                items.append(key)
        
        return items
    