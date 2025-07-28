from utils.constants import TRUE, FALSE, OR, AND, INTEGER, REAL, STRING, BOOLEAN, FLOAT

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
            return str(val).lower() in (TRUE.lower(), FALSE.lower())
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
    try:
        flag = left == right
        if flag is True:
            return TRUE
        return FALSE
    except Exception as e:
        return FALSE
