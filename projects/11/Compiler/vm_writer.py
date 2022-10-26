        
def write_push(segment, int) -> str:
    return f"push {segment} {int}\n"

def write_pop(segment, int) -> str:
    return f"pop {segment} {int}\n"

def write_arithmetic(operation) -> str:
    return f"{operation}\n"

def write_label(label: str) -> str:
    return f"label {label}\n"

def write_goto(label: str) -> str:
    return f"goto {label}\n"

def write_if(label: str) -> str:
    return f"if-goto {label}\n"

def write_call(name: str, n_args: int) -> str:
    return f"call {name} {n_args}\n"

def write_function(name: str, n_vars: int) -> str:
    return f"function {name} {n_vars}\n"

def write_return() -> str:
    return "return\n"
