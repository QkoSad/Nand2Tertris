# rotate through 1 file or a directory to open and translate all of the .vm files
import os

trueCounter = 0
falseCounter = 0
staticCounter = 16


def clear_file(temp_string_cf, asmfile):  # clears the empty lines, comments and spaces and writes them in a string
    for line in asmfile:
        f = 0
        if line == '\n':  # removes empty lines
            continue
        for index in range(len(line)):
            if line[index] == "/" and line[index + 1] == '/':  # checks if it is comment
                if f == 1:  # maybe a problem if the last element of a line is / since it will stay
                    temp_string_cf += '\n'
                break
            if line[index] != ' ':  # removes all of the whitespaces except newlines
                temp_string_cf += line[index]
                f = 1
    return temp_string_cf


def push(line):
    global tempString1
    if line[4:8] == 'this':
        number = int(line[8:])
        line = '@' + str(number) + '\nD=A\n@THIS\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:8] == 'that':
        number = int(line[8:])
        line = '@' + str(number) + '\nD=A\n@THAT\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:8] == 'temp':
        number = int(line[8:])
        number += 5
        line = '@' + str(number) + '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:9] == 'local':
        number = int(line[9:])
        line = '@' + str(number) + '\nD=A\n@LCL\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:10] == 'static':
        number = int(line[10:])
        line = '@' + name1 + '.' + str(number) + '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:11] == 'pointer':
        number = int(line[11:])
        number += 3
        line = '@' + str(number) + '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:12] == 'argument':
        number = int(line[12:])
        line = '@' + str(number) + '\nD=A\n@ARG\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    elif line[4:12] == 'constant':
        number = line[12:]
        line = '@' + str(number) + '\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    tempString1 += line


def pop(line):
    global SP
    global tempString1
    if line[3:7] == 'this':
        number = int(line[7:])
        line = '@' + str(number) + '\nD=A\n@THIS\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@THIS\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@THIS\nM=M-D\n'
    elif line[3:7] == 'that':
        number = int(line[7:])
        line = '@' + str(number) + '\nD=A\n@THAT\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@THAT\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@THAT\nM=M-D\n'
    elif line[3:7] == 'temp':
        number = int(line[7:])
        number = number + 5
        line = '@SP\nM=M-1\nA=M\nD=M\n@' + str(number) + '\nM=D\n'
    elif line[3:8] == 'local':
        number = int(line[8:])
        line = '@' + str(number) + '\nD=A\n@LCL\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@LCL\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@LCL\nM=M-D\n'
    elif line[3:9] == 'static':
        number = int(line[9:])
        line = '@SP\nM=M-1\nA=M\nD=M\n@' + name1 + '.' + str(number) + '\nM=D\n'
    elif line[3:10] == 'pointer':
        number = int(line[10:])
        number = number + 3
        line = '@SP\nM=M-1\nA=M\nD=M\n@' + str(number) + '\nM=D\n'
    elif line[3:11] == 'argument':
        number = int(line[11:])
        line = '@' + str(number) + '\nD=A\n@ARG\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@ARG\nM=M-D\n'
    tempString1 += line


def aritmetic(line):
    global trueCounter
    global falseCounter
    global tempString1
    if line == 'add':
        line = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M+D\n"
    elif line == 'sub':
        line = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M-D\n"
    elif line == 'neg':
        line = "@SP\nA=M\nA=A-1\nM=-M\n"
    elif line == 'eq':
        line = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@TRUE' + str(
            trueCounter) + '\nD;JEQ\n@SP\nA=M\nA=A-1\nM=0\n@FALSE' + str(
            falseCounter) + '\n0;JMP\n(TRUE' + str(trueCounter) + ')\n@SP\nA=M\nA=A-1\nM=-1\n(FALSE' + str(
            falseCounter) + ')\n'
        trueCounter += 1
        falseCounter += 1
    elif line == 'gt':
        line = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@TRUE' + str(
            trueCounter) + '\nD;JGT\n@SP\nA=M\nA=A-1\nM=0\n@FALSE' + str(
            falseCounter) + '\n0;JMP\n(TRUE' + str(trueCounter) + ')\n@SP\nA=M\nA=A-1\nM=-1\n(FALSE' + str(
            falseCounter) + ')\n'
        trueCounter += 1
        falseCounter += 1
    elif line == 'lt':
        line = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@TRUE' + str(
            trueCounter) + '\nD;JLT\n@SP\nA=M\nA=A-1\nM=0\n@FALSE' + str(
            falseCounter) + '\n0;JMP\n(TRUE' + str(trueCounter) + ')\n@SP\nA=M\nA=A-1\nM=-1\n(FALSE' + str(
            falseCounter) + ')\n'
        trueCounter += 1
        falseCounter += 1
    elif line == 'and':
        line = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M&D\n"
    elif line == 'or':
        line = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M|D\n"
    elif line == 'not':
        line = "@SP\nA=M\nA=A-1\nM=!M\n"
    tempString1 += line


line, tempString = '', ''
tempString1 = ''
aritmeticList3 = ['add', 'sub', 'neg', 'and', 'not']
aritmeticList2 = ['or', 'gt', 'lt', 'eq']
yourpath = 'C:/Users/AGrudev/Desktop/n2t/nand2tetris/projects/07/MemoryAccess/StaticTest'
for root, dirs, files in os.walk(yourpath, topdown=False):
    for name in files:
        if name[-3:] == '.vm':
            name1 = name
            print(name)
            with open(yourpath + '/' + name, "r+") as vmfile:
                tempString = clear_file(tempString, vmfile)
            print(tempString)
            for j in tempString:  # zapisva liniqta v string koito posle se obrabotva
                if j != '\n':
                    line += j
                else:
                    # breakpoint()
                    if line[:4] == 'push':
                        push(line)
                        line = ''
                    elif line[:3] == 'pop':
                        pop(line)
                        line = ''
                    elif line[:2] in aritmeticList2 or line[:3] in aritmeticList3:
                        aritmetic(line)
                        line = ''

with open(yourpath + '/' + name1[:-3] + '.asm', 'w+') as newfile:
    newfile.write(tempString1)

print(tempString1)
