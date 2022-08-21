// this pushes the value at a segment + index to the location where SP is pointing.
// 
// 

// get index value into D
@20
D=A
// get pointer of segment and add index
@LCL
A=D+A
D=M
// put onto stack and increment SP
@SP
M=M+1
A=M-1
M=D
