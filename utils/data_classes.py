import abc
from enum import Enum
from typing import List
from utils.constants import *


class SymbolTypes(Enum):
    INTEGER = "INTEGER"
    STRING = "STRING"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"


class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __str__(self) -> str:
        return f'Token({self.type}, {self.value})'


class NodeVisitor(object):
    def visit(self, node):
        class_name = type(node).__name__
        method_name = 'visit_' + class_name
        method = getattr(self, method_name)
        return method(node)


class AST:
    pass

class Node(AST):  # Define or import Node class before LogMe
    pass
class ReturnStat(AST):
    pass

class ShowCall(AST):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'ShowCall({self.value})'
class Valuable(abc.ABC):
    def get_value(self):
        pass


class Num(AST):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return f'Num({self.token.type}, {self.value})'


class Str(AST):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return f'Str({self.value})'


class StrOp(AST):
    def __init__(self, left, add: Token, right):
        self.left = left
        self.add = add
        self.right = right

    def __str__(self):
        return f'StrOp({self.left}, {self.add}, {self.right})'


class BinOp(AST):
    def __init__(self, left, op: Token, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return f'BinOp({self.left}, {self.op.type}, {self.right})'


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

    def __str__(self):
        return f'UnaryOp({self.op}, {self.expr})'


class Compound(AST):
    def __init__(self):
        self.children = []

    def add(self, node):
        self.children.append(node)

    def get_children(self):
        return self.children

    def __str__(self):
        res = ""
        for node in self.children:
            res += str(node) + ", "

        return f'Compound({res})'


class Var(AST, Valuable):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

    def get_value(self):
        return self.value

    def __str__(self):
        return f'Var({self.value})'


class Assign(AST):
    def __init__(self, left: Var, op: Token, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return f'Assign({self.left}, :=, {self.right})'


class NoOp(AST):
    def __str__(self):
        return 'NoOp()'


class VarDecs(AST):
    def __init__(self, variables, base_type: Token, value=None):
        self.variables = variables
        self.token = self.type = base_type
        self.value = value

    def get_declarations(self):
        return self.variables

    def get_type(self) -> Token:
        return self.type

    def get_value(self):
        return self.value

    def get_var_names(self):
        return ", ".join([token.value for token in self.variables])

    def __str__(self):
        res = ""
        for var in self.variables:
            res += var.value + ', '
        return f'VarDecs(({res}), {self.type.value}, {self.value})'


class Program(AST):
    def __init__(self, block):
        self.block = block

    def __str__(self):
        return f'Program({self.block})'


class Block(AST):
    def __init__(self, var_decs: list, compound_statement: Compound):
        self.var_decs = var_decs
        self.compound_statement = compound_statement

    def __str__(self):
        res = ""
        for dec in self.var_decs:
            res += str(dec) + ", "
        return f'Program({res}, {self.compound_statement})'


class AbstractSymbol(abc.ABC):
    def __init__(self, name, *args):
        self.name = name

    def is_symbol(self):
        return isinstance(self, Symbol)

    def is_function(self):
        return isinstance(self, FunctionDecl)


class FunctionDecl(AbstractSymbol, Valuable):
    def __init__(self, proc_name, params, block, return_expression=None):
        super(FunctionDecl, self).__init__(proc_name)
        self.name = proc_name
        self.block = block
        self.params = params if params is not None else []
        self.return_expression = return_expression

    def get_value(self):
        return str(self)

    def __str__(self):
        return f'FunctionDecl({self.name}, {self.params}, {self.block}, {self.return_expression})'


class FunctionCall(AST):
    def __init__(self, name, actual_params, token):
        self.name = name
        self.actual_params = actual_params
        self.token = token

    def __str__(self):
        res = ""
        for param in self.actual_params:
            res += str(param) + ", "
        return f'FunctionCall({self.name}, {res}, {self.token})'


class Symbol(AbstractSymbol):
    def __init__(self, name, value=None, symbol_type=None):
        super().__init__(name)
        self.name = name
        self.value = value
        self.type = symbol_type

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}, {self.value}, {self.type})'

    __repr__ = __str__


class VarSymbol(Symbol):
    def __init__(self, name, value, base_type=None):
        super().__init__(name, value, base_type)



# class BooleanSymbol:
#     def __init__(self, value, token=None):
#         self.value = value
#         self.token = token

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)


class NotOp(AST):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f'NotOp({self.expr})'


class BoolOp(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f'{self.__class__.__name__}({self.left}, {self.right})'


class BoolOr(BoolOp):
    def __init__(self, left, right):
        super().__init__(left, right)


class BoolAnd(BoolOp):
    def __init__(self, left, right):
        super().__init__(left, right)


class BoolNotEqual(BoolOp):
    def __init__(self, left, right):
        super().__init__(left, right)


class BoolGreaterThan:
    def __init__(self, left, right, token=None):
        self.left = left
        self.right = right
        self.token = token



class BoolGreaterThanOrEqual(BoolOp):
    def __init__(self, left, right):
        super().__init__(left, right)


class BoolLessThan:
    def __init__(self, left, right, token=None):
        self.left = left
        self.right = right
        self.token = token



class BoolLessThanOrEqual(BoolOp):
    def __init__(self, left, right):
        super().__init__(left, right)


class BoolIsEqual(BoolOp):
    def __init__(self, left, right):
        super().__init__(left, right)


class IfBlock(AST):
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block

    def __str__(self):
        return f'IfBlock({self.expr}, {self.block})'


class IfStat(AST):
    def __init__(self, if_blocks: List, else_block):
        self.if_blocks = if_blocks
        self.else_block = else_block

    def __str__(self):
        stats = ""
        for if_block in self.if_blocks:
            stats += str(if_block) + ","
        return f'IfStat({stats}, {self.else_block})'


class ForLoop(AST):
    def __init__(self, base: Assign, bool_expr, then, block: Block):
        self.base = base
        self.bool_expr = bool_expr
        self.then = then
        self.block = block

    def __str__(self):
        return f'ForLoop({self.base}, {self.bool_expr}, {self.then}, {self.block})'


class Break(AST):
    def __init__(self):
        pass

    def __str__(self):
        return f'Break()'


class Breakable(abc.ABC):
    def is_terminated(self):
        raise Exception('is_terminated() should be implemented in child class')


class Countable:
    recursion_counter = 0

    def count_recursion(self):
        self.recursion_counter += 1

    def get_recursion_count(self):
        return self.recursion_counter


class BeforeNodeVisitor(NodeVisitor, Breakable, Countable):
    def visit(self, node):
        if self.is_terminated():
            return None
        self.count_recursion()
        return super().visit(node)


class ReturnStat(AST):
    def __init__(self, base_expr):
        self.base_expr = base_expr

    def __str__(self):
        return f'ReturnStat({self.base_expr})'
class ShowStatement:
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return f"SHOW {self.expression}"

    def __repr__(self):
        return str(self)
class WhileLoop(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
            return str(self)

    def __str__(self):
        return f'WhileLoop({self.condition}, {self.body})'
    
class DoWhileLoop(Node):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

    def __str__(self):
        return f'DoWhileLoop({self.body}, {self.condition})'
class ArrayAccess(AST):
    def __init__(self, array_var: Var, index: AST):
        self.array_var = array_var
        self.index = index

    def __str__(self):
        return f'ArrayAccess({self.array_var}, {self.index})'
class CaseBlock(AST):
    """Represents a single case block in a switch statement"""
    def __init__(self, value, statements):
        self.value = value  # The value to match against (can be None for default)
        self.statements = statements  # List of statements to execute
        self.is_default = value is None
    
    def __str__(self):
        if self.is_default:
            return f'DefaultCase({self.statements})'
        return f'CaseBlock({self.value}, {self.statements})'

class SwitchStatement(AST):
    """Represents a complete switch statement"""
    def __init__(self, expression, case_blocks):
        self.expression = expression  # Expression to evaluate and match
        self.case_blocks = case_blocks  # List of CaseBlock objects
        
    def get_default_case(self):
        """Returns the default case block if it exists"""
        for case in self.case_blocks:
            if case.is_default:
                return case
        return None
    
    def get_case_blocks(self):
        """Returns non-default case blocks"""
        return [case for case in self.case_blocks if not case.is_default]
    
    def __str__(self):
        cases_str = ", ".join(str(case) for case in self.case_blocks)
        return f'SwitchStatement({self.expression}, [{cases_str}])'
class ConstDeclaration(AST):
    """Represents a constant declaration"""
    def __init__(self, variables, base_type: Token, value):
        self.variables = variables  # List of variable tokens
        self.token = self.type = base_type
        self.value = value  # Required value (constants must be initialized)
        
    def get_declarations(self):
        return self.variables
    
    def get_type(self) -> Token:
        return self.type
    
    def get_value(self):
        return self.value
    
    def get_var_names(self):
        return ", ".join([token.value for token in self.variables])
    
    def __str__(self):
        res = ""
        for var in self.variables:
            res += var.value + ', '
        return f'ConstDeclaration(({res}), {self.type.value}, {self.value})'

class ConstSymbol(Symbol):
    """Symbol representing a constant - immutable after initialization"""
    def __init__(self, name, value, base_type=None):
        super().__init__(name, value, base_type)
        self.is_constant = True
    
    def __str__(self):
        return f'ConstSymbol({self.name}, {self.value}, {self.type})'
class RealisticSymbol(AST):
    """Represents a realistic truth value - between true and false"""
    def __init__(self, value, token=None, probability=0.5):
        self.value = value  # Should be REALISTIC
        self.token = token
        self.probability = probability  # 0.0 to 1.0, default 0.5 for pure realistic
    
    def __str__(self):
        return f'RealisticSymbol({self.value}, probability={self.probability})'

class BooleanSymbol:
    """Enhanced to handle realistic values"""
    def __init__(self, value, token=None, probability=None):
        self.value = value
        self.token = token
        # For TRUE: probability = 1.0
        # For FALSE: probability = 0.0  
        # For REALISTIC: probability = 0.5 (or custom value)
        if probability is None:
            if value == TRUE:
                self.probability = 1.0
            elif value == FALSE:
                self.probability = 0.0
            elif value == REALISTIC:
                self.probability = 0.5
            else:
                self.probability = 0.5
        else:
            self.probability = probability
    
    def is_realistic(self):
        return self.value == REALISTIC
    
    def __str__(self):
        return f'BooleanSymbol({self.value}, probability={self.probability})'

class HypothesisStatement(AST):
    """Represents a hypothesis in a proof"""
    def __init__(self, hypothesis_name: str, statement=None):
        self.hypothesis_name = hypothesis_name  # Name/label for the hypothesis
        self.statement = statement              # The assumed statement
        self.is_assumption = True               # Mark as assumption (not proven)
        
    def get_name(self):
        return self.hypothesis_name
    
    def get_statement(self):
        return self.statement
    
    def is_hypothesis(self):
        return self.is_assumption
    
    def __str__(self):
        return f'Hypothesis({self.hypothesis_name}, {self.statement})'
class ProofDeclaration(AST):
    """Represents a proof for a theorem"""
    def __init__(self, theorem_name: str, proof_steps=None):
        self.theorem_name = theorem_name      # Which theorem this proves
        self.proof_steps = proof_steps or []  # List of proof steps
        self.is_complete = False              # Whether proof is complete (ends with QED)
        self.is_valid = False                 # Whether proof is logically valid
        
    def get_theorem_name(self):
        return self.theorem_name
    
    def get_proof_steps(self):
        return self.proof_steps
    
    def add_step(self, step):
        self.proof_steps.append(step)
    
    def mark_complete(self):
        self.is_complete = True
    
    def mark_valid(self):
        self.is_valid = True
        self.is_complete = True
    
    def is_proof_complete(self):
        return self.is_complete
    
    def is_proof_valid(self):
        return self.is_valid
    
    def __str__(self):
        status = "VALID" if self.is_valid else ("COMPLETE" if self.is_complete else "INCOMPLETE")
        return f'Proof({self.theorem_name}, {len(self.proof_steps)} steps, {status})'
    
class ProofStep(AST):
    """Enhanced proof step that can reference axioms"""
    def __init__(self, step_type: str, statement=None, justification=None, 
                 hypothesis_name=None, test_name=None, axiom_name=None):
        self.step_type = step_type              # "statement", "hypothesis", "test", "axiom", etc.
        self.statement = statement              # The statement being made
        self.justification = justification      # How this step is justified
        self.hypothesis_name = hypothesis_name  # Name if this is a hypothesis
        self.test_name = test_name             # Name if this is a test
        self.axiom_name = axiom_name           # Name if this references an axiom
        
    def get_step_type(self):
        return self.step_type
    
    def get_statement(self):
        return self.statement
    
    def get_justification(self):
        return self.justification
    
    def get_hypothesis_name(self):
        return self.hypothesis_name
    
    def get_test_name(self):
        return self.test_name
    
    def get_axiom_name(self):
        return self.axiom_name
    
    def is_hypothesis_step(self):
        return self.step_type == "hypothesis"
    
    def is_test_step(self):
        return self.step_type == "test"
    
    def is_axiom_step(self):
        return self.step_type == "axiom"
    
    def __str__(self):
        if self.hypothesis_name:
            return f'ProofStep({self.step_type}, {self.hypothesis_name}: {self.statement})'
        elif self.test_name:
            return f'ProofStep({self.step_type}, test_{self.test_name}: {self.statement})'
        elif self.axiom_name:
            return f'ProofStep({self.step_type}, axiom_{self.axiom_name}: {self.statement})'
        return f'ProofStep({self.step_type}, {self.statement})'

class QEDStatement(AST):
    """Represents the end of proof marker"""
    def __init__(self):
        pass
    
    def __str__(self):
        return 'QED()'

class TheoremDeclaration(AST):
    """Enhanced theorem declaration that can be linked to proofs"""
    def __init__(self, theorem_name: str, statement=None):
        self.theorem_name = theorem_name
        self.statement = statement
        self.is_proven = False
        self.dependencies = []
        self.proof = None  # Link to associated proof
        
    def get_name(self):
        return self.theorem_name
    
    def get_statement(self):
        return self.statement
    
    def set_proof(self, proof: ProofDeclaration):
        self.proof = proof
        if proof.is_proof_valid():
            self.mark_proven()
    
    def get_proof(self):
        return self.proof
    
    def mark_proven(self):
        self.is_proven = True
    
    def is_theorem_proven(self):
        return self.is_proven
    
    def add_dependency(self, theorem_name):
        self.dependencies.append(theorem_name)
    
    def get_dependencies(self):
        return self.dependencies
    
    def __str__(self):
        status = "PROVEN" if self.is_proven else "UNPROVEN"
        proof_info = f" (with proof)" if self.proof else ""
        return f'Theorem({self.theorem_name}, {self.statement}, {status}{proof_info})'


class TestStatement(AST):
    """Represents a test of a hypothesis or assumption"""
    def __init__(self, test_name: str, hypothesis_name: str, test_condition=None):
        self.test_name = test_name              # Name of the test
        self.hypothesis_name = hypothesis_name  # Which hypothesis to test
        self.test_condition = test_condition    # Condition to test against
        self.test_result = None                 # Result of the test (pass/fail/uncertain)
        self.is_executed = False                # Whether test has been run
        
    def get_test_name(self):
        return self.test_name
    
    def get_hypothesis_name(self):
        return self.hypothesis_name
    
    def get_test_condition(self):  # ✅ This method was missing
        return self.test_condition
    
    def set_test_result(self, result):
        self.test_result = result
        self.is_executed = True
    
    def get_test_result(self):
        return self.test_result
    
    def is_test_passed(self):
        return self.test_result == "PASS"
    
    def is_test_failed(self):
        return self.test_result == "FAIL"
    
    def is_test_uncertain(self):
        return self.test_result == "UNCERTAIN"
    
    def __str__(self):
        status = f"({self.test_result})" if self.is_executed else "(not executed)"
        return f'Test({self.test_name}, {self.hypothesis_name}, {status})'

class AxiomDeclaration(AST):
    """Represents an axiom - a fundamental truth that doesn't need proof"""
    def __init__(self, axiom_name: str, statement=None, description=None):
        self.axiom_name = axiom_name        # Name of the axiom
        self.statement = statement          # The axiom statement (always true)
        self.description = description      # Optional description
        self.is_axiom = True               # Mark as axiom (self-evident)
        self.is_proven = True              # Axioms are considered proven by definition
        
    def get_name(self):
        return self.axiom_name
    
    def get_statement(self):
        return self.statement
    
    def get_description(self):
        return self.description
    
    def is_axiom_declaration(self):
        return self.is_axiom
    
    def is_axiom_proven(self):
        return self.is_proven  # Axioms are always "proven"
    
    def __str__(self):
        desc = f", '{self.description}'" if self.description else ""
        return f'Axiom({self.axiom_name}, {self.statement}{desc})'
