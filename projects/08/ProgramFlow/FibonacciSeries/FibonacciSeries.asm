//push argument 1
@1
D=A
@ARG
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
//pop pointer 1
@SP
AM=M-1
D=M
@THAT
M=D
//push constant 0
@0
D=A
@SP
M=M+1
A=M-1
M=D
//pop that 0
@0
D=A
@THAT
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push constant 1
@1
D=A
@SP
M=M+1
A=M-1
M=D
//pop that 1
@1
D=A
@THAT
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
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
//pop argument 0
@0
D=A
@ARG
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
($MAIN_LOOP_START)
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
//jump to ($COMPUTE_ELEMENT) if top stack item is not false (0)
@SP
AM=M-1
D=M
@$COMPUTE_ELEMENT
D;JNE
//jump to ($END_PROGRAM)
@$END_PROGRAM
0;JMP
($COMPUTE_ELEMENT)
//push that 0
@0
D=A
@THAT
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
//push that 1
@1
D=A
@THAT
A=D+M
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
//pop that 2
@2
D=A
@THAT
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//push pointer 1
@THAT
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
//add
M=D+M
//pop pointer 1
@SP
AM=M-1
D=M
@THAT
M=D
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
//pop argument 0
@0
D=A
@ARG
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
//jump to ($MAIN_LOOP_START)
@$MAIN_LOOP_START
0;JMP
($END_PROGRAM)
(END)
@END
0;JMP