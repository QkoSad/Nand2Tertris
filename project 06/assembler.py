def a_instruct(string):  # covert the A instruction to bits
    string = string.strip('@\n')
    x = "{0:b}".format(int(string))  # convert the number to binary, problem if the number is too big
    while len(x) < 16:  # need to be 16 bits and 1 for \n
        x = "0" + x
    return x  # return th 16 bit value


def c_instruct(string):  # priema edna liniq koeto e edna instrukciq i q prevryshta v bit kod
    string = string + "\n"
    flag1, flag2, p = 0, 0, 0
    dest_s = ''
    comp_s = ''
    jump_s = ''
    for c in range(len(string)):
        if string[c] == '=':  # ako ima ravno znachi predi nego ima  destination 
            i = 0
            flag1 = 1  # diga flag za destination
            while i < c:
                p = c
                dest_s += string[i]
                i += 1
            dest_s = destDic.get(dest_s)  # convert t to Destination
        if string[c] == ';':  # ako ima ; znachi predi nego ima  computation 
            flag2 = 1  # diga flag za Jump
            if flag1 == 0:  # ako flaga za destination ne e dignat zapochvame ot nachaloto na liniqta
                p = 0
            else:  # ako e zapochvame ot kydeto e ravnoto koeto se pazi vyv var i
                p = i
            while p < c:
                comp_s += string[p]
                p += 1
            comp_s = compDic.get(comp_s)  # convert t1 to Computation

        if string[c] == '\n':
            if flag2 == 1:  # ako ima flag za jump to vzimame stoinosta na jumpa
                j = p + 1
                while j < c:
                    jump_s += string[j]
                    j += 1
                jump_s = jumpDic.get(jump_s)
            else:  # ako nqma togava vzima stoinosta na computationa
                j = i + 1
                while j < c:
                    comp_s += string[j]
                    j += 1
                comp_s = compDic.get(comp_s)
    final_result = '111' + comp_s  # dobavqme 111 koeto e standart za C instrukt i computation bez koeto nqma instrukciq
    if dest_s != '':  # ako e imalo dest go dobavqme
        final_result = final_result + dest_s
    else:  # inache dobavqme 3 nuli
        final_result = final_result + '000'
    if jump_s != '':  # ako e imalo jump go dobavqme
        final_result = final_result + jump_s
    else:  # inache dobavqme 3 nuli
        final_result = final_result + '000'
    return final_result


def check_a_or_c(temp_string):
    line = ''
    temp_string1 = ''
    for j in temp_string:  # zapisva liniqta v string koito posle se obrabotva
        if j != '\n':
            line += j
        else:
            for index in range(len(line)):  # proverqva vseki simvol ot liniqta
                if line[index] == "@":  # ako liniqta zapochva s @ znachi e a instrukciq
                    temp_string1 += a_instruct(line) + '\n'
                    line = ''
                    break
                else:  # ako ne zapochva s @ znachi e C instrukciq
                    temp_string1 += c_instruct(line) + '\n'
                    line = ''
                    break
    return temp_string1


def clear_file(temp_string_cf):  # clears the empty lines, comments and spaces and writes them in a string
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


def label(temp_string):  # removes the labels and adds them to the dictionary writes all in a string
    line = ''
    temp_string_l = ''
    global rowasm
    for j in temp_string:  # zapisva liniqta v string koito posle se obrabotva
        if j != '\n':
            line += j
        else:
            f = 0
            for index in range(len(line)):  # loops through the lines char by char
                if line[index] == "(":
                    # checks if it is a label, will be a problem if there is only "(" and no closing bracket alse need to check label syntax
                    if bool(labelDic.get(line.strip('()'))) == False:  # check if label is already in the Dictionary
                        labelDic[line.strip("()")] = str(rowasm)  # adds the label to the dictionary
                        rowasm -= 1  # need to pay attention to the counting cause im not sure
                        f = 1
                        break  # brake so i don't write this line in the string since it needs to be removed
            if f != 1:
                temp_string_l += line
                temp_string_l += '\n'
            rowasm += 1
            line = ''
    return temp_string_l


def variable(temp_string):  # replaces the variables with the correct address
    global variableCount
    line = ''
    temp_string_v = ''
    for j in temp_string:  # zapisva liniqta v string koito posle se obrabotva
        if j != '\n':
            line += j
        else:
            for index in range(len(line)):
                if line[index] == '@' and numbers.find(line[index + 1]) < 0:  # checks if the line holds a variable
                    if bool(labelDic.get(line.strip('@'))):  # check if variable is already in the Dictionary
                        line = '@' + labelDic[line.strip('@')]  # replaces the variable with address i hope
                    else:
                        labelDic[line.strip('@')] = str(variableCount)  # if isn't it adds it
                        line = '@' + str(variableCount)  # replaces the variable with address i hope
                        variableCount += 1  # increases the variable counter so i don't write them all in address 16
                    break
            temp_string_v += line + '\n'  # appends the line to the string
            line = ''
    return temp_string_v


destDic = {'None': '000',
           'M': '001',
           'D': '010',
           'MD': '011',
           'A': '100',
           'AM': '101',
           'AD': '110',
           'AMD': '111', }  # contains all destinations and their bit equivalent
jumpDic = {'None': '000',
           'JGT': '001',
           'JQE': '010',
           'JGE': '011',
           'JLT': '100',
           'JNE': '101',
           'JLE': '110',
           'JMP': '111', }  # contains all jumps and their bit equivalent
compDic = {'0': '0101010',
           '1': '0111111',
           '-1': '0111010',
           'D': '0001100',
           'A': '0110000',
           '!D': '0001101',
           '!A': '0110001',
           '-D': '0001111',
           '-A': '0110011',
           'D+1': '0011111',
           'A+1': '0110111',
           'D-1': '0001110',
           'A-1': '0110010',
           'D+A': '0000010',
           'D-A': '0010011',
           'A-D': '0000111',
           'D&A': '0000000',
           'D|A': '0010101',
           'M': '1110000',
           '!M': '1110001',
           '-M': '1110011',
           'M+1': '1110111',
           'M-1': '1110010',
           'D+M': '1000010',
           'D-M': '1010011',
           'M-D': '1000111',
           'D&M': '1000000',
           'D|M': '1010101',
           }  # contains all computations and their bit equivalent
tempString = ''  # create empty string
rowasm = 0
numbers = '0123456789'  # used to check if given instruction calls to variable
variableCount = 16  # keeps count of the variable address

labelDic = {'SP': '0',
            'LCL': '1',
            'ARG': '2',
            'THIS': '3',
            'THAT': '4',
            'SCREEN': '16384',
            'KBD': '24576',
            'R0': '0',
            'R1': '1',
            'R2': '2',
            'R3': '3',
            'R4': '4',
            'R5': '5',
            'R6': '6',
            'R7': '7',
            'R8': '8',
            'R9': '9',
            'R10': '10',
            'R11': '11',
            'R12': '12',
            'R13': '13',
            'R14': '14',
            'R15': '15',
            }  # dictionary containing Labels and Variables in format: AddressNumber : LabelName/ VariableName
with open("C:/Users/AGrudev/Desktop/n2t/nand2tetris/projects/06/pong/Pong.asm", "r+") as asmfile:
    tempString = clear_file(tempString)
print(tempString + '----------')

tempString = label(tempString)
print(tempString + '----------')

tempString = variable(tempString)
print(tempString + '----------')

tempString = check_a_or_c(tempString)
print(tempString + '----------')

with open("C:/Users/AGrudev/Desktop/n2t/nand2tetris/projects/06/pong/Pong.hack", "w+") as destfile:
    destfile.write(tempString)
