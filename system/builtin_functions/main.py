from utils.constants import TRUE, FALSE, OR, AND, INTEGER, REAL, STRING, BOOLEAN, FLOAT,REALISTIC

_delta_for_floats = 1 / 1e8


class BuiltinFunctions:
    @staticmethod
    def print(*items):
        print(*items)


_builtin_functions = BuiltinFunctions()


def is_system_function(name):
    if hasattr(_builtin_functions, name):
        return True
    else:
        return False


def call_system_function(name, *args, **kwargs):
    func = getattr(_builtin_functions, name)
    return func(*args, *kwargs)


def evaluate_bool_expression(left, op, right):
    if left not in (TRUE, FALSE):
        raise ValueError('left not in true,false')

    if right not in (TRUE, FALSE):
        raise ValueError('right not in true,false')

    if op not in (OR, AND):
        raise ValueError('op not in or, and')

    if op is OR:
        if left is TRUE or right is TRUE:
            return TRUE
        return FALSE
    else:
        if left is TRUE and right is TRUE:
            return TRUE
        return FALSE


def not_bool(bool_val):
    if bool_val not in (TRUE, FALSE):
        raise ValueError("value error")

    if bool_val is TRUE:
        return FALSE
    return TRUE


def is_val_of_type(val, base_type):
    if base_type not in (INTEGER, FLOAT, STRING, BOOLEAN):
        raise ValueError('base_type must be int,str,bool or real type')

    if val is None:
        return True

    if base_type in (INTEGER, FLOAT):
        if base_type == INTEGER:
            try:
                return isinstance(int(val), int) and str(val).count('.') == 0
            except Exception as e:
                return False
        else:
            try:
                return isinstance(float(val), float)
            except Exception as e:
                return False
    elif base_type is STRING:
        return isinstance(val, str)
    elif base_type is BOOLEAN:
        try:
            if isinstance(val, str):
                val_upper = val.upper()
                return val_upper in ["TRUE", "FALSE", "REALISTIC"]
            return val in ["TRUE", "FALSE", "REALISTIC"]
        except Exception as e:
            return False


def not_equal(left, right):
    try:
        flag = left != right
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return TRUE


def bool_or(left, right):
    try:
        return evaluate_bool_expression(left, OR, right)
    except Exception as e:
        return FALSE


def bool_and(left, right):
    try:
        return evaluate_bool_expression(left, AND, right)
    except Exception as e:
        return FALSE


def bool_greater_than(left, right):
    try:
        flag = int(left) > int(right) or (float(left) - float(right) > _delta_for_floats)
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return FALSE


def bool_greater_than_or_equal(left, right):
    try:
        flag = int(left) >= int(right) and (float(left) - float(right) > -_delta_for_floats)
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return FALSE


def bool_less_than(left, right):
    try:
        flag = int(left) < int(right) or (float(left) - float(right) < -_delta_for_floats)
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return FALSE


def bool_less_than_or_equal(left, right):
    try:
        flag = int(left) <= int(right) and (float(left) - float(right) < _delta_for_floats)
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return FALSE


def bool_is_equal(left, right):
    """Enhanced equality for realistic values"""
    try:
        # Handle realistic comparisons
        if isinstance(left, str) and left == REALISTIC:
            return realistic_equal(left, right)
        if isinstance(right, str) and right == REALISTIC:
            return realistic_equal(left, right)
        
        # Normal comparison
        flag = left == right
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return REALISTIC  # When uncertain, return realistic

def realistic_not(bool_val):
    """NOT operation for three-valued logic"""
    if bool_val == TRUE:
        return FALSE
    elif bool_val == FALSE:
        return TRUE
    elif bool_val == REALISTIC:
        return REALISTIC  # NOT realistic = realistic
    else:
        raise ValueError("Invalid boolean value for NOT operation")

def realistic_or(left, right):
    """OR operation for three-valued logic"""
    # Truth table for realistic OR:
    # TRUE OR anything = TRUE
    # FALSE OR FALSE = FALSE
    # FALSE OR REALISTIC = REALISTIC
    # FALSE OR TRUE = TRUE
    # REALISTIC OR REALISTIC = REALISTIC
    
    if left == TRUE or right == TRUE:
        return TRUE
    elif left == FALSE and right == FALSE:
        return FALSE
    elif left == REALISTIC or right == REALISTIC:
        return REALISTIC
    else:
        raise ValueError("Invalid boolean values for OR operation")

def realistic_and(left, right):
    """AND operation for three-valued logic"""
    # Truth table for realistic AND:
    # FALSE AND anything = FALSE
    # TRUE AND TRUE = TRUE
    # TRUE AND REALISTIC = REALISTIC
    # TRUE AND FALSE = FALSE
    # REALISTIC AND REALISTIC = REALISTIC
    
    if left == FALSE or right == FALSE:
        return FALSE
    elif left == TRUE and right == TRUE:
        return TRUE
    elif left == REALISTIC or right == REALISTIC:
        return REALISTIC
    else:
        raise ValueError("Invalid boolean values for AND operation")

def realistic_equal(left, right):
    """Equality comparison with realistic values"""
    if left == right:
        return TRUE
    elif left == REALISTIC or right == REALISTIC:
        return REALISTIC  # Uncertain equality
    else:
        return FALSE

def realistic_not_equal(left, right):
    """Not equal comparison with realistic values"""
    equality_result = realistic_equal(left, right)
    return realistic_not(equality_result)
def bool_not_equal(left, right):
    """Enhanced not equal for realistic values"""
    try:
        equality_result = bool_is_equal(left, right)
        if equality_result == REALISTIC:
            return REALISTIC
        return realistic_not(equality_result)
    except Exception as e:
        return REALISTIC