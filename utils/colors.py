
class Colors:
    """ANSI color codes for console output"""
    # Text Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background Colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    
    # Styles
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Proof Assistant Specific Colors
    THEOREM_DECLARED = BRIGHT_BLUE
    THEOREM_PROVEN = BRIGHT_GREEN
    PROOF_STEP = CYAN
    ERROR = BRIGHT_RED
    WARNING = BRIGHT_YELLOW
    INFO = WHITE
    SUCCESS = BRIGHT_GREEN

class ProofConsole:
    """Console utilities for proof assistant output"""
    
    @staticmethod
    def theorem_declared(theorem_name, statement, is_proven=False):
        """Print theorem declaration with colors"""
        status_color = Colors.THEOREM_PROVEN if is_proven else Colors.YELLOW
        status_text = "PROVEN" if is_proven else "UNPROVEN"
        
        print(f"{Colors.THEOREM_DECLARED}{Colors.BOLD}[THEOREM]{Colors.RESET} "
              f"{Colors.BRIGHT_WHITE}{theorem_name}{Colors.RESET}")
        print(f"   Statement: {Colors.CYAN}{statement}{Colors.RESET}")
        print(f"   Status: {status_color}{status_text}{Colors.RESET}")
    
    @staticmethod
    def proof_start(theorem_name, steps_count):
        """Print proof start with colors"""
        print(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}[PROOF]{Colors.RESET} "
              f"for theorem '{Colors.BRIGHT_WHITE}{theorem_name}{Colors.RESET}':")
        print(f"   Steps: {Colors.BRIGHT_CYAN}{steps_count}{Colors.RESET}")
    
    @staticmethod
    def proof_step(step_number, statement):
        """Print individual proof step with colors"""
        print(f"   {Colors.BRIGHT_YELLOW}{step_number}.{Colors.RESET} "
              f"{Colors.PROOF_STEP}{statement}{Colors.RESET}")
    
    @staticmethod
    def proof_complete(theorem_name):
        """Print proof completion message"""
        print(f"   {Colors.SUCCESS}{Colors.BOLD}[✓] Proof complete (QED found){Colors.RESET}")
        print(f"   {Colors.SUCCESS}{Colors.BOLD}[SUCCESS]{Colors.RESET} "
              f"Theorem '{Colors.BRIGHT_WHITE}{theorem_name}{Colors.RESET}' is now "
              f"{Colors.SUCCESS}{Colors.BOLD}PROVEN{Colors.RESET}!")
    
    @staticmethod
    def proof_incomplete(theorem_name):
        """Print proof incomplete message"""
        print(f"   {Colors.ERROR}{Colors.BOLD}[✗] Proof incomplete (missing QED){Colors.RESET}")
    
    @staticmethod
    def error(message):
        """Print error message"""
        print(f"{Colors.ERROR}{Colors.BOLD}[ERROR]{Colors.RESET} {Colors.ERROR}{message}{Colors.RESET}")
    
    @staticmethod
    def warning(message):
        """Print warning message"""
        print(f"{Colors.WARNING}{Colors.BOLD}[WARNING]{Colors.RESET} {Colors.WARNING}{message}{Colors.RESET}")
    
    @staticmethod
    def info(message):
        """Print info message"""
        print(f"{Colors.INFO}{message}{Colors.RESET}")
    
    @staticmethod
    def success(message):
        """Print success message"""
        print(f"{Colors.SUCCESS}{Colors.BOLD}[SUCCESS]{Colors.RESET} {Colors.SUCCESS}{message}{Colors.RESET}")
