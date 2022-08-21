// test of pop mechanism

// get index
@20
D=A
// get pointer of segment and add index
@LCL
D=D+M
// store pointer in a temp register R13
@R13
M=D
// get value in stack
@SP
AM=M-1
D=M
// save to location that R13 points to
@R13
A=M
M=D