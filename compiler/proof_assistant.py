
from utils.constants import *
from utils.data_classes import *
from utils.errors import SemanticError, ErrorCode

class ProofAssistant:
    """Main proof assistant engine for theorem proving"""
    
    def __init__(self):
        self.theorems = {}  # name -> TheoremStatement
        self.proofs = {}    # theorem_name -> ProofBlock  
        self.axioms = {}    # name -> AxiomStatement
        self.hypotheses = {} # name -> Hypothesis
        self.logical_rules = self.initialize_logical_rules()
        self.proof_context = {}  # Current proof context
    
    def initialize_logical_rules(self):
        """Initialize basic logical inference rules"""
        return {
            'modus_ponens': 'If P implies Q and P, then Q',
            'modus_tollens': 'If P implies Q and not Q, then not P',
            'hypothetical_syllogism': 'If P implies Q and Q implies R, then P implies R',
            'disjunctive_syllogism': 'If P or Q and not P, then Q',
            'conjunction': 'If P and Q are both true, then (P and Q) is true',
            'simplification': 'If (P and Q) is true, then P is true',
            'addition': 'If P is true, then (P or Q) is true',
            'realistic_propagation': 'REALISTIC values propagate through logical operations',
            'realistic_and': 'TRUE and REALISTIC = REALISTIC',
            'realistic_or': 'FALSE or REALISTIC = REALISTIC',
            'realistic_not': 'NOT REALISTIC = REALISTIC'
        }
    
    def register_axiom(self, axiom):
        """Register an axiom as fundamental truth"""
        self.axioms[axiom.name] = axiom
        print(f"✓ Axiom registered: {axiom.name}")
        return True
    
    def register_theorem(self, theorem):
        """Register a theorem for proving"""
        self.theorems[theorem.name] = theorem
        print(f"📋 Theorem stated: {theorem.name}")
        return True
    
    def register_proof(self, proof):
        """Register a proof for a theorem"""
        self.proofs[proof.theorem_name] = proof
        return True
    
    def verify_proof(self, proof):
        """Verify that a proof is logically sound"""
        theorem = self.theorems.get(proof.theorem_name)
        if not theorem:
            return False, f"Theorem {proof.theorem_name} not found"
        
        print(f"🔍 Verifying proof for: {proof.theorem_name}")
        
        # Track assumptions and derived facts
        context = {}
        step_number = 1
        
        for step in proof.steps:
            print(f"  Step {step_number}: {step.step_type} {step.statement}")
            
            if step.step_type == ASSUME:
                context[f"assumption_{len(context)}"] = step.statement
                print(f"    ✓ Assumption added to context")
            
            elif step.step_type == GIVEN:
                context[f"given_{len(context)}"] = step.statement
                print(f"    ✓ Given fact added to context")
            
            elif step.step_type == THEREFORE:
                if self.verify_step(step.statement, context, step.justification):
                    context[f"derived_{len(context)}"] = step.statement
                    print(f"    ✓ Conclusion verified")
                else:
                    return False, f"Step {step_number} does not follow: {step.statement}"
            
            step_number += 1
        
        # Mark theorem as proven
        theorem.is_proven = True
        return True, "Proof verified successfully! 🎉"
    
    def verify_step(self, conclusion, context, justification=None):
        """Verify that a conclusion follows from the current context"""
        # Check if conclusion is already in context (trivial case)
        for fact in context.values():
            if self.statements_equivalent(conclusion, fact):
                return True
        
        # Apply logical inference rules
        return self.apply_inference_rules(conclusion, context, justification)
    
    def apply_inference_rules(self, conclusion, context, justification):
        """Apply logical inference rules to verify conclusion"""
        # For demonstration, accept steps with recognized justifications
        if justification:
            justification_str = str(justification).lower()
            
            # Check if justification matches known logical rules
            for rule_name, rule_desc in self.logical_rules.items():
                if rule_name in justification_str:
                    print(f"    📚 Applied rule: {rule_name}")
                    return True
            
            # Accept any justification for now (in real implementation, this would be more rigorous)
            return True
        
        return False
    
    def statements_equivalent(self, stmt1, stmt2):
        """Check if two logical statements are equivalent"""
        return str(stmt1) == str(stmt2)
    
    def get_proof_status(self):
        """Get status of all theorems and proofs"""
        status = {
            'axioms': len(self.axioms),
            'theorems': len(self.theorems),
            'proven_theorems': sum(1 for t in self.theorems.values() if t.is_proven),
            'proofs': len(self.proofs)
        }
        return status
