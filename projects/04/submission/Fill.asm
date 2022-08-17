// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Set screen word counter to 0
@word
M=0

(START) // Infinite loop

	// If key is pressed (not equal to zero), go to PRESSED
	@KBD
	D=M
	@PRESSED
	D;JNE
	
	// The lines between here and PRESSED will only
	// execute if there is no key pressed
	
	// If word = 0, go to START (screen is already empty)
	@word
	D=M
	
	@START
	D;JEQ
	
	// else decrement word ,set address at screen+word to 0, and then go to start
	@word
	M=M-1
	
	@word
	D=M
	@SCREEN
	A=A+D
	M=0	

	@START
	0;JMP
	
(PRESSED)
	// If word = 8192, go to START (screen is already full)
	@8192
	D=A
	@word
	D=M-D
	
	@START
	D;JEQ

	// else set address at screen+word to -1, increment word, and then go to start
	@word
	D=M
	@SCREEN
	A=A+D
	M=-1
	
	@word
	M=M+1
	
	@START
	0;JMP