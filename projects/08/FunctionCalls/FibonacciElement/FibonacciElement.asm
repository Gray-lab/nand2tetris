@261
D=A
@SP
M=D
@1
D=-A
@LCL
M=D
@2
D=-A
@ARG
M=D
@3
D=-A
@THIS
M=D
@4
D=-A
@THAT
M=D
@Sys.init
0;JMP
// Define function Main.fibonacci with 0 variables
(Main.fibonacci)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
//push constant 2
@2
D=A
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
//lt
D=M-D
M=-1
@ltTrue0
D;JLT
@SP
A=M-1
M=0
(ltTrue0)
//jump to (Main.fibonacci$IF_TRUE) if top stack item is not false (0)
@SP
AM=M-1
D=M
@Main.fibonacci$IF_TRUE
D;JNE
//jump to (Main.fibonacci$IF_FALSE)
@Main.fibonacci$IF_FALSE
0;JMP
(Main.fibonacci$IF_TRUE)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
// return from function
@LCL
D=M
@R14
M=D
@5
A=D-A
D=M
@R15
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R14
AM=M-1
D=M
@THAT
M=D
@R14
AM=M-1
D=M
@THIS
M=D
@R14
AM=M-1
D=M
@ARG
M=D
@R14
AM=M-1
D=M
@LCL
M=D
@R15
A=M
0;JMP
(Main.fibonacci$IF_FALSE)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
//push constant 2
@2
D=A
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
// call function Main.fibonacci with 1 args
@Main.fibonacci$ret.0
D=A
@SP
M=M+1
A=M-1
M=D
// push LCL
@LCL
D=M
@SP
M=M+1
A=M-1
M=D
// push ARG
@ARG
D=M
@SP
M=M+1
A=M-1
M=D
// push THIS
@THIS
D=M
@SP
M=M+1
A=M-1
M=D
// push THAT
@THAT
D=M
@SP
M=M+1
A=M-1
M=D
@5
D=A
@1
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.0)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
//push constant 1
@1
D=A
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
// call function Main.fibonacci with 1 args
@Main.fibonacci$ret.2
D=A
@SP
M=M+1
A=M-1
M=D
// push LCL
@LCL
D=M
@SP
M=M+1
A=M-1
M=D
// push ARG
@ARG
D=M
@SP
M=M+1
A=M-1
M=D
// push THIS
@THIS
D=M
@SP
M=M+1
A=M-1
M=D
// push THAT
@THAT
D=M
@SP
M=M+1
A=M-1
M=D
@5
D=A
@1
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Main.fibonacci$ret.2)
//pop_2
@SP
AM=M-1
D=M
@SP
A=M-1
//add
M=D+M
// return from function
@LCL
D=M
@R14
M=D
@5
A=D-A
D=M
@R15
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R14
AM=M-1
D=M
@THAT
M=D
@R14
AM=M-1
D=M
@THIS
M=D
@R14
AM=M-1
D=M
@ARG
M=D
@R14
AM=M-1
D=M
@LCL
M=D
@R15
A=M
0;JMP
// Define function Sys.init with 0 variables
(Sys.init)
//push constant 4
@4
D=A
@SP
M=M+1
A=M-1
M=D
// call function Main.fibonacci with 1 args
@Sys.init$ret.0
D=A
@SP
M=M+1
A=M-1
M=D
// push LCL
@LCL
D=M
@SP
M=M+1
A=M-1
M=D
// push ARG
@ARG
D=M
@SP
M=M+1
A=M-1
M=D
// push THIS
@THIS
D=M
@SP
M=M+1
A=M-1
M=D
// push THAT
@THAT
D=M
@SP
M=M+1
A=M-1
M=D
@5
D=A
@1
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(Sys.init$ret.0)
(Sys.init$WHILE)
//jump to (Sys.init$WHILE)
@Sys.init$WHILE
0;JMP
(END)
@END
0;JMP
