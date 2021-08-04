import os


def clear_file(clearfile):
    temp_string_cf = ''  # clears the empty lines, comments and spaces and writes them in a string
    for vmline in clearfile:
        flag = 0
        if vmline == '\n':
            continue
        for index in range(len(vmline)):
            if vmline[index:index + 2] == '//':
                if flag == 1:
                    temp_string_cf += '\n'
                break
            if flag == 1 and vmline[index:index + 2] == '  ':
                temp_string_cf += '\n'
                break
            temp_string_cf += vmline[index]
            flag = 1
    return temp_string_cf


def push(pushline, funcname):
    if 'this' in pushline:
        number = int(pushline[10:])
        pushline = '@' + str(number) + '\nD=A\n@THIS\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push THIS\n'
    elif 'that' in pushline:
        number = int(pushline[10:])
        pushline = '@' + str(number) + '\nD=A\n@THAT\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push THAT\n'
    elif 'temp' in pushline:
        number = int(pushline[10:])
        number += 5
        pushline = '@' + str(number) + '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push TMP\n'
    elif 'local' in pushline:
        number = int(pushline[11:])
        pushline = '@' + str(number) + '\nD=A\n@LCL\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push LOCAL\n'
    elif 'static' in pushline:
        breakpoint()
        number = int(pushline[12:])
        pushline = '@' + funcname + '.' + str(number) + '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push STATIC\n'
    elif 'pointer' in pushline:
        number = int(pushline[13:])
        number += 3
        pushline = '@' + str(number) + '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push POINTER\n'
    elif 'argument' in pushline:
        number = int(pushline[14:])
        pushline = '@' + str(number) + '\nD=A\n@ARG\nA=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push ARGUMENT\n'
    elif 'constant' in pushline:
        number = pushline[14:]
        pushline = '@' + str(number) + '\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//push CONSTANT\n'
    return pushline


def pop(popline, funcname):
    if 'this' in popline:
        number = int(popline[9:])
        popline = '@' + str(number) + '\nD=A\n@THIS\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@THIS\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@THIS\nM=M-D\n//pop THIS\n'
    elif 'that' in popline:
        number = int(popline[9:])
        popline = '@' + str(number) + '\nD=A\n@THAT\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@THAT\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@THAT\nM=M-D\n//pop THAT\n'
    elif 'temp' in popline:
        number = int(popline[9:])
        number = number + 5
        popline = '@SP\nM=M-1\nA=M\nD=M\n@' + str(number) + '\nM=D\n//pop TMP\n'
    elif 'local' in popline:
        number = int(popline[10:])
        popline = '@' + str(number) + '\nD=A\n@LCL\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@LCL\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@LCL\nM=M-D\n//pop LOCAL\n'
    elif 'static' in popline:
        breakpoint()
        number = int(popline[11:])
        popline = '@SP\nM=M-1\nA=M\nD=M\n@' + funcname + '.' + str(number) + '\nM=D\n//pop STATIC\n'
    elif 'pointer' in popline:
        number = int(popline[12:])
        number = number + 3
        popline = '@SP\nM=M-1\nA=M\nD=M\n@' + str(number) + '\nM=D\n//pop POINTER\n'
    elif 'argument' in popline:
        number = int(popline[13:])
        popline = '@' + str(number) + '\nD=A\n@ARG\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n' + '@' + str(
            number) + '\nD=A\n@ARG\nM=M-D\n//pop ARG\n'
    return popline


def aritmetic(armline):
    global trueCounter
    global falseCounter
    if armline == 'add':
        armline = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M+D\n//ADD\n"
    elif armline == 'sub':
        armline = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M-D\n//SUB\n"
    elif armline == 'neg':
        armline = "@SP\nA=M\nA=A-1\nM=-M\n//NEG\n"
    elif armline == 'eq':
        armline = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@TRUE' + str(
            trueCounter) + '\nD;JEQ\n@SP\nA=M\nA=A-1\nM=0\n@FALSE' + str(
            falseCounter) + '\n0;JMP\n(TRUE' + str(trueCounter) + ')\n@SP\nA=M\nA=A-1\nM=-1\n(FALSE' + str(
            falseCounter) + ')\n//EQ\n'
        trueCounter += 1
        falseCounter += 1
    elif armline == 'gt':
        armline = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@TRUE' + str(
            trueCounter) + '\nD;JGT\n@SP\nA=M\nA=A-1\nM=0\n@FALSE' + str(
            falseCounter) + '\n0;JMP\n(TRUE' + str(trueCounter) + ')\n@SP\nA=M\nA=A-1\nM=-1\n(FALSE' + str(
            falseCounter) + ')\n//GT\n'
        trueCounter += 1
        falseCounter += 1
    elif armline == 'lt':
        armline = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@TRUE' + str(
            trueCounter) + '\nD;JLT\n@SP\nA=M\nA=A-1\nM=0\n@FALSE' + str(
            falseCounter) + '\n0;JMP\n(TRUE' + str(trueCounter) + ')\n@SP\nA=M\nA=A-1\nM=-1\n(FALSE' + str(
            falseCounter) + ')\n//LT\n'
        trueCounter += 1
        falseCounter += 1
    elif armline == 'and':
        armline = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M&D\n//AND\n"
    elif armline == 'or':
        armline = "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M|D\n//OR\n"
    elif armline == 'not':
        armline = "@SP\nA=M\nA=A-1\nM=!M\n//NOT\n"
    return armline


def label(labelline):
    labelline = '(' + func_label_name + '$' + labelline[6:] + ')\n//LABEL\n'
    return labelline


def goto(gotoline):
    gotoline = '@' + func_label_name + '$' + gotoline[5:] + '\n0;JMP\n//GOTO\n'
    return gotoline


def if_goto(ifline):
    ifline = '@SP\nM=M-1\nA=M\nD=M\n@' + func_label_name + '$' + ifline[8:] + '\nD;JNE\n//IFGOTO\n'
    return ifline


def define_func(funcline):
    global func_label_name
    def_func_list = funcline.rsplit(' ')
    func_label_name = def_func_list[1]
    funcline = '(' + def_func_list[1] + ')\n'
    for ind in range(int(def_func_list[2])):
        funcline += '@0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n//DEFINEFUNC\n'
    return funcline


def call_func(callline):
    global f
    call_func_list = callline.rsplit(' ')
    callline = '@' + call_func_list[1] + str(f) + 'RA\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    callline += '@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    callline += '@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    callline += '@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    callline += '@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    callline += '@SP\nD=M\n@' + call_func_list[2] + '\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n'
    callline += '@SP\nD=M\n@LCL\nM=D\n'
    callline += '@' + call_func_list[1] + '\n0;JMP\n'
    callline += '(' + call_func_list[1] + str(f) + 'RA)\n//CALLFUNC\n'
    f += 1
    return callline


def return_func(returnline):
    returnline = '@LCL\nD=M\n@R13\nM=D\n'
    returnline += '@5\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@R14\nM=D\n'
    returnline += '@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n'
    returnline += '@ARG\nD=M+1\n@SP\nM=D\n'
    returnline += '@R13\nM=M-1\nA=M\nD=M\n@THAT\nM=D\n'
    returnline += '@R13\nM=M-1\nA=M\nD=M\n@THIS\nM=D\n'
    returnline += '@R13\nM=M-1\nA=M\nD=M\n@ARG\nM=D\n'
    returnline += '@R13\nM=M-1\nA=M\nD=M\n@LCL\nM=D\n'
    returnline += '@R14\nA=M\n0;JMP\n//RETURN\n'
    return returnline


def iterate(name_iterate, yourpath_iterate):
    line = ''
    new_string = ''
    with open(yourpath_iterate + '/' + name_iterate + '.vm', "r+") as vmfile:
        string_iterate = clear_file(vmfile)
    print(string_iterate)
    for j in string_iterate:  # zapisva liniqta v string koito posle se obrabotva
        if j != '\n':
            line += j
        else:
            if line[:4] == 'push':
                new_string += push(line, name_iterate)
                line = ''
            elif line[:3] == 'pop':
                new_string += pop(line, name_iterate)
                line = ''
            elif line[:2] in aritmeticList2 or line[:3] in aritmeticList3:
                new_string += aritmetic(line)
                line = ''
            elif line[:5] == 'label':
                new_string += label(line)
                line = ''
            elif line[:4] == 'goto':
                new_string += goto(line)
                line = ''
            elif line[:7] == 'if-goto':
                new_string += if_goto(line)
                line = ''
            elif line[:8] == 'function':
                new_string += define_func(line)
                line = ''
            elif line[:4] == 'call':
                new_string += call_func(line)
                line = ''
            elif line[:6] == 'return':
                new_string += return_func(line)
                line = ''
    return new_string


trueCounter = 0
falseCounter = 0
staticCounter = 16
f = 0
func_label_name = ''
aritmeticList3 = ['add', 'sub', 'neg', 'and', 'not']
aritmeticList2 = ['or', 'gt', 'lt', 'eq']
yourpath = 'C:/Users/AGrudev/Desktop/nand2tetris/projects/08/FunctionCalls/StaticsTest'
folder_name = ''
for c in reversed(yourpath):
    if c != '/':
        folder_name += c
    else:
        break
folder_name = folder_name[::-1]

nameslist = []
for root, dirs, files in os.walk(yourpath, topdown=False):
    for name in files:
        tempString = ''
        if name[-3:] == '.vm':
            nameslist += [name[:-3]]

sysstring, functstring = '', ''

for i in nameslist:
    if i == 'Sys':
        sysstring = iterate(i, yourpath)
    else:
        functstring += iterate(i, yourpath)
tempString1 ='@256\nD=A\n@SP\nM=D\n@Sys.init\n0;JMP\n'+ sysstring + functstring
with open(yourpath + '/' + folder_name + '.asm', 'w+') as newfile:  # tva tqbva da se kazva papkata ne faila
    # TODO before i write the whole things i think i should write  SP=256 call Sys.init in assembler pretty sure i should
    newfile.write(tempString1)
# TODO make it run more than 1 file
