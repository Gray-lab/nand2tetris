//push constant 111
@111
D=A
@SP
M=M+1
A=M-1
M=D
//push constant 333
@333
D=A
@SP
M=M+1
A=M-1
M=D
//push constant 888
@888
D=A
@SP
M=M+1
A=M-1
M=D
//pop static 8
@SP
AM=M-1
D=M
@.0
M=D//pop static 3
@SP
AM=M-1
D=M
@.1
M=D//pop static 1
@SP
AM=M-1
D=M
@.2
M=D//push static 3
@.1
D=M
@SP
M=M+1
A=M-1
M=D
//push static 1
@.2
D=M
@SP
M=M+1
A=M-1
M=D
//pop_2
@SP
AM=M-1
D=M
@SP
A=M-1
//sub
M=M-D
//push static 8
@.0
D=M
@SP
M=M+1
A=M-1
M=D
//pop_2
@SP
AM=M-1
D=M
@SP
A=M-1
//add
M=D+M
(END)
@END
0;JMP
