// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.
// ------------------------------
// We need to add R0 together R1 times
// 2 * 4 = 2 + 2 + 2 + 2

	// Reset R2
	@R2
	M=0

	// LOAD D<-R1
	@R1
	D=M

	// if R1 is 0, jump to END
	@END
	D;JEQ

	// Initialize counter
	@i
	M=D
	
(LOOP) //while i>0, add R0 to R2
	@R0
	D=M
	@R2
	M=M+D
	
	// Decrement counter
	@i
	D=M-1
	M=D
	
	// Check condition
    @LOOP
	D;JGT
	
(END)
	@END
	0;JMP
