@R2
M=0
@sum
M=0
(LOOP)
@1
D=M
@END
D;JEQ 	// if R1==0 goto end
@R0
D=M    	// D=R0
@sum
M=M+D  	// sum=sum+R0
@R1
M=M-1	//R1=R1-1
@sum
D=M
@R2
M=D
@LOOP
0;JMP
(END)
@END
0;JMP