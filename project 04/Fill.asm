@END //check if button is pressed
0;JMP

(BLACK)
//start= 16384 the start of the screen memory
@SCREEN
D=A
@start
M=D

//n=8,192 this is the memory for the display =addreass of the keyboard - address of the screen
@8192
D=A
@n
M=D

//i=0 this is the index for each group of pixels
@i
M=0

(LOOP1)
//if i==n goto end
@i
D=M
@n
D=D-M
@END
D;JEQ

//start+1=-1 set each group of pixels to -1 which is = 111111111111
@start
D=M
@i
A=D+M
M=-1

// increment i by 1
@i
M=M+1

// go back to the start of the loop
@LOOP1
0;JMP

(WHITE)
//start= 16384 the start of the screen memory
@SCREEN
D=A
@start
M=D

//n=8,192 this is the memory for the display =addreass of the keyboard - address of the screen
@8192
D=A
@n
M=D

//i=0 this is the index for each group of pixels
@i
M=0

(LOOP2)
//if i==n goto end
@i
D=M
@n
D=D-M
@END
D;JEQ

//start+1=-1 set each group of pixels to 0 which is = 00000000
@start
D=M
@i
A=D+M
M=0

// increment i by 1
@i
M=M+1

// go back to the start of the loop
@LOOP2
0;JMP

//check if button is pressed
(END)
@KBD
D=M
@WHITE
D;JEQ
@KBD
D=M
@BLACK
D;JNE
@END
0;JMP