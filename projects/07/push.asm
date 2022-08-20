// this pushes the value at RAM[10] to the location of SP - set to RAM[20] for this example.
// set RAM[10] to non zero value

@10
D=M
@0
M=M+1
A=M-1
M=D
