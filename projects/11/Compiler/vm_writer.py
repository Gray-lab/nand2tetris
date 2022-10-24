class VMwriter():
    def __init__ (self, out_file: str) -> None:
        with open(out_file, "w") as out:
            self.file = out
        
    def write_push(self, segment, int) -> None:
        self.file.write(f"push {segment} {int}\n")

    def write_pop(self, segment, int) -> None:
        self.file.write(f"pop {segment} {int}\n")

    def write_arithmetic(self, operation) -> None:
        self.file.write(f"{operation}\n")

    def write_label(self, label: str) -> None:
        self.file.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        self.file.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        self.file.write(f"if-goto {label}\n")

    def write_call(self, name: str, n_args: int) -> None:
        self.file.write(f"call {name} {n_args}\n")

    def write_function(self, name: str, n_vars: int) -> None:
        self.file.write(f"function {name} {n_vars}\n")

    def write_return(self) -> None:
        self.file.write("return\n")
