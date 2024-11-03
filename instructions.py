import sys
import re

class instruction:
    def __init__(self, opcode, order, frames, parent):
        self.parent = parent
        self.opcode = opcode
        self.order = order
        self.args = [] # Array of arguments of the instruction
        self.frames = frames

    def execute(self): # Execute the instructions     
        self.opcode = self.opcode.upper() # Make the opcode uppercase

        if(self.opcode == "CREATEFRAME"):
            self.CREATEFRAME()
        elif(self.opcode == "PUSHFRAME"):
            self.PUSHFRAME()
        elif(self.opcode == "POPFRAME"):
            self.POPFRAME() 
        elif(self.opcode == "MOVE"):
            self.MOVE()          
        elif(self.opcode == "DEFVAR"):
            self.DEFVAR()
        elif(self.opcode == 'READ'):
            self.READ()
        elif(self.opcode == 'WRITE' or self.opcode == 'DPRINT'): # Dont know about Dprint put it there for now
            self.WRITE_DPRINT()
        elif(self.opcode == 'PUSHS'):
            self.PUSHS()
        elif(self.opcode == 'POPS'):
            self.POPS()
        elif(self.opcode == 'ADD' or self.opcode == 'SUB' or self.opcode == 'MUL' or self.opcode == 'IDIV'):
            self.ARITHMETIC()
        elif(self.opcode == 'GT' or self.opcode == 'LT' or self.opcode == 'EQ'):
            self.COMPARE()
        elif(self.opcode == 'AND' or self.opcode == 'OR'):
            self.LOGICAL()
        elif(self.opcode == 'NOT'):
            self.NOT()
        elif(self.opcode == 'INT2CHAR'):
            self.INT2CHAR()
        elif(self.opcode == 'STRI2INT'):
            self.STRI2INT()
        elif(self.opcode == 'CONCAT'):
            self.CONCAT()
        elif(self.opcode == 'STRLEN'):
            self.STRLEN()
        elif(self.opcode == 'GETCHAR'):
            self.GETCHAR()
        elif(self.opcode == 'SETCHAR'):
            self.SETCHAR()
        elif(self.opcode == 'TYPE'):
            self.TYPE()
        elif(self.opcode == 'LABEL'):
            self.LABEL()
        elif(self.opcode == 'JUMP'):
            self.JUMP()
        elif(self.opcode == 'JUMPIFEQ'):
            self.JUMPIFEQ()       
        elif(self.opcode == 'JUMPIFNEQ'):
            self.JUMPIFNEQ()
        elif(self.opcode == 'CALL'):
            self.CALL()
        elif(self.opcode == 'RETURN'):
            self.RETURN()          
        elif(self.opcode == 'EXIT'):
            self.EXIT()
        elif(self.opcode == 'BREAK'):
            self.BREAK()

    #--------------- Functions for each instruction ---------------
    def CREATEFRAME(self):
        self.parent.frames.create_temporary_frame()
    
    def PUSHFRAME(self):
        self.parent.frames.push_frame()
    
    def POPFRAME(self):
        self.parent.frames.pop_frame()
    
    def DEFVAR(self):
        frame, name = self.args[0].value.split('@')
        frame_def = self.parent.frames.get_right_frame(frame)
        
        if(frame_def is None):
            sys.stderr.write("Chyba, pokus o vytvorenie premennej na neexistujucom ramci\n")
            exit(55)
        else:
            if(name in frame_def):
                sys.stderr.write("Chyba, premenna uz existuje na ramci\n")
                exit(52)
            else:
                frame_def[name] = {'type': None, 'value': None}
        
    def MOVE(self):
        frame, name = self.args[0].value.split('@')
        type_of_var, data = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)   
        self.parent.frames.set_var(type_of_var, data, frame, name)
        
    def READ(self):     
        frame, name = self.args[0].value.split('@')
        type_of_var, data = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)

        if(name not in self.parent.frames.get_right_frame(frame)): # check if the name of the variable exists on the frame
            sys.stderr.write("Chyba, premenna neexistuje na ramci\n")
            exit(54)
        else:
            if(type_of_var != 'type'): # check if the second argument is type
                sys.stderr.write("Chyba, neznamy typ operandu\n")
                exit(53)
            
            if(data == 'int'):
                try: 
                    loaded_val = str(int(input())) #value which we got from input file/stdin
                except:
                    loaded_val = 'nil'
                    self.args[1].value = 'nil'
                    self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name)
                else:
                    self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name)
                
            elif(data == 'bool'):
                try:
                    loaded_val = str(input())
                    if (loaded_val.lower() == 'true'):
                        self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name)
                    else:
                        loaded_val = 'false'
                        self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name)       
                except:
                    loaded_val = 'nil'
                    self.args[1].value = 'nil'
                    self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name)               

            elif(data == 'string'):
                try:
                    loaded_val = str(input())
                except:
                    loaded_val = 'nil'
                    self.args[1].value = 'nil'
                    self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name)   
                else:
                    self.parent.frames.set_var(self.args[1].value, loaded_val, frame, name) 
            else:
                sys.stderr.write("Chyba, najdeny datovy typ nebol rozpoznany\n")
                exit(54)
 
    def WRITE_DPRINT(self):
        type_of_var, data = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value)

        def replacement_char(match): # function for replacing octal numbers with their ascii characters
            char_code = int(match.group(0)[1:])
            return chr(char_code)  
                
        if (type_of_var == 'string'): # if the type of the variable is string, we have to replace octal numbers with their ascii characters (white spaces)
            data = re.sub(r'\\\d{3}', replacement_char, data)
   
        if (data is None):
            sys.stderr.write("Dana premenna nebola definovana\n")
            exit(56) 
        else:
            if (data == 'nil' and type_of_var == 'nil'):
                data = ''
            if (self.opcode == 'WRITE'):
                print(data, end='')
            elif(self.opcode == 'DPRINT'):
                sys.stderr.write(data)
                
    def PUSHS(self):
        type_of_var, data = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value)
        self.parent.stack_for_data.append((type_of_var, data))
        
    def POPS(self):
        try:
            type_of_var, data = self.parent.stack_for_data.pop()
        except IndexError:
            sys.stderr.write("Pokus o 'pop' prazdneho datoveho zasobniku\n")
            exit(56)   
        frame, name = self.args[0].value.split('@')
        self.parent.frames.set_var(type_of_var, data, frame, name)
    
    def ARITHMETIC(self):
            frame, name = self.args[0].value.split('@')
            data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value) # <arg2>
            data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value) # <arg3> 
                   
            if(data_type_1 != 'int' or data_type_2 != 'int'):
                sys.stderr.write("Aritmeticke instrukcie pracuju len s datovym typom int\n")
                exit(53)
            else:
                try:
                    data_1 = int(data_1)
                    data_2 = int(data_2)
                except:
                    sys.stderr.write("Hodnota premennej nie je typu int\n")
                    exit(32)
                
                if(self.opcode == 'ADD'):
    
                    self.parent.frames.set_var('int', str(int(data_1) + int(data_2)), frame, name)
                elif(self.opcode == 'SUB'):
                    self.parent.frames.set_var('int', str(int(data_1) - int(data_2)), frame, name)
                elif(self.opcode == 'MUL'):
                    self.parent.frames.set_var('int', str(int(data_1) * int(data_2)), frame, name)
                elif(self.opcode == 'IDIV'):
                    if(int(data_2) == 0):
                        sys.stderr.write("Chyba, delenie nulou\n")
                        exit(57)
                    else:
                        self.parent.frames.set_var('int', str(int(data_1) // int(data_2)), frame, name)

    def COMPARE(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value)  
        
        if (data_type_1 == data_type_2):
            if (self.opcode == 'EQ'):
                if (data_1 == data_2):
                    self.parent.frames.set_var('bool', 'true', frame, name)
                elif (data_1 != data_2):
                    self.parent.frames.set_var('bool', 'false', frame, name)
            elif (self.opcode in ['GT', 'LT'] and (data_type_1 == 'nil' or data_type_2 == 'nil')):
                sys.stderr.write("Chyba, nie je dovolene porovnavat typy nil medzi sebou s instrukciou GT a LT\n")
                exit(53)
            elif (self.opcode == 'GT'):
                if (data_type_1 == 'nil'):
                    self.parent.frames.set_var('bool', 'false', frame, name)
                elif (data_type_1 == 'string'):
                    if (data_1 > data_2):
                        self.parent.frames.set_var('bool', 'true', frame, name)
                    else:
                        self.parent.frames.set_var('bool', 'false', frame, name) 
                elif (data_type_1 == 'bool'):
                    if (data_1 == 'true' and data_2 == 'false'):
                        self.parent.frames.set_var('bool', 'true', frame, name)
                    else:
                        self.parent.frames.set_var('bool', 'false', frame, name) 
                elif (data_type_1 == 'int'):
                    if (int(data_1) > int(data_2)):
                        self.parent.frames.set_var('bool', 'true', frame, name)
                    else:
                        self.parent.frames.set_var('bool', 'false', frame, name)
            elif (self.opcode == 'LT'):
                if (data_type_1 == 'nil'):
                    self.parent.frames.set_var('bool', 'false', frame, name)
                elif (data_type_1 == 'string'):
                    if (data_1 < data_2):
                        self.parent.frames.set_var('bool', 'true', frame, name)
                    else:
                        self.parent.frames.set_var('bool', 'false', frame, name) 
                elif (data_type_1 == 'bool'):
                    if (data_1 == 'false' and data_2 == 'true'):
                        self.parent.frames.set_var('bool', 'true', frame, name)
                    else:
                        self.parent.frames.set_var('bool', 'false', frame, name) 
                elif (data_type_1 == 'int'):
                    if (int(data_1) < int(data_2)):
                        self.parent.frames.set_var('bool', 'true', frame, name)
                    else:
                        self.parent.frames.set_var('bool', 'false', frame, name)
        elif (self.opcode == 'EQ' and (data_type_1 == 'nil' or data_type_2 == 'nil')):
            self.parent.frames.set_var('bool', 'false', frame, name)
        else:
            sys.stderr.write("Chyba, dane typy sa nedaju porovnat\n")
            exit(53)
        
    def LOGICAL(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value)
        
        if (data_type_1 == 'bool' and data_type_2 == 'bool'):
            if (self.opcode == 'AND'):
                if (data_1 == 'true' and data_2 == 'true'):
                    self.parent.frames.set_var('bool', 'true', frame, name)
                else:
                    self.parent.frames.set_var('bool', 'false', frame, name)
            elif (self.opcode == 'OR'):
                if (data_1 == 'true' or data_2 == 'true'):
                    self.parent.frames.set_var('bool', 'true', frame, name)
                else:
                    self.parent.frames.set_var('bool', 'false', frame, name)
        else:
            sys.stderr.write("Chyba, instrukcie AND a OR mozu pracovat len s datovym typom bool\n")
            exit(53)
    
    def NOT(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        
        if (data_type_1 == 'bool'):
            if (data_1 == 'true'):
                self.parent.frames.set_var('bool', 'false', frame, name)
            else:
                self.parent.frames.set_var('bool', 'true', frame, name)
        else:
            sys.stderr.write("Chyba, instrukcia NOT moze pracovat len s datovym typom bool\n")
            exit(53)
                    
    def INT2CHAR(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)      
        
        if (data_type_1 == 'int'):
            try:
                self.parent.frames.set_var('string', chr(int(data_1)), frame, name)
            except ValueError:
                sys.stderr.write("Chyba, hodnota je mimo rozsahu znakov\n")
                exit(58)
        else:
            sys.stderr.write("Chyba, instrukcia INT2CHAR moze pracovat len s datovym typom int\n")
            exit(53)

    def STRI2INT(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value)
        
        if (data_type_1 == 'string' and data_type_2 == 'int'):
            if (int(data_2) < 0 or int(data_2) > len(data_1)-1):
                sys.stderr.write("Chyba, index je mimo rozsahu zadaneho retazca\n")
                exit(58)
            else:
                self.parent.frames.set_var('int', ord(data_1[int(data_2)]), frame, name)
        else:
            sys.stderr.write("Chyba, instrukcia STRI2INT moze pracovat len s datovymi typmi int a string\n")
            exit(53)
     
    def CONCAT(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value)   
        
        if (data_type_1 == 'string' and data_type_2 == 'string'):
            if(data_1 is None):
                data_1 = ''
                self.parent.frames.set_var('string', data_1 + data_2, frame, name)
            if(data_2 is None):
                data_2 = ''    
                self.parent.frames.set_var('string', data_1 + data_2, frame, name)
            else:
                self.parent.frames.set_var('string', data_1 + data_2, frame, name)
        else:
            sys.stderr.write("Chyba, instrukcia CONCAT moze pracovat len s datovym typom string\n")
            exit(53)
            
    def STRLEN(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)  
        
        if (data_type_1 == 'string'):
            self.parent.frames.set_var('int', len(data_1) if data_1 != None else 0, frame, name)
        else:
            sys.stderr.write("Chyba, instrukcia STRLEN moze pracovat len s datovym typom string\n")
            exit(53)
            
    def GETCHAR(self):
        frame, name = self.args[0].value.split('@')
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value)   
        
        if (data_type_1 == 'string' and data_type_2 == 'int'):
            if (int(data_2) < 0 or int(data_2) > len(data_1)-1):
                sys.stderr.write("Chyba, index je mimo rozsahu zadaneho retazca\n")
                exit(58)
            else:
                self.parent.frames.set_var('string', data_1[int(data_2)], frame, name)
        else:
            sys.stderr.write("Chyba, instrukcia GETCHAR moze pracovat len s datovymi typmi int a string\n")
            exit(53)
    
    def SETCHAR(self):
        frame, name = self.args[0].value.split('@')
        data_type_0, data_0 = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value)
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value)
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value)       
        if (data_type_0 == 'string' and data_type_1 == 'int' and data_type_2 == 'string'):  
            if (int(data_1) < 0 or data_type_0 == '' or int(data_1) > len(data_0)-1): #Check if index is in range of string and if string is not empty
                sys.stderr.write("Chyba, index je mimo rozsahu zadaneho retazca\n")
                exit(58)
            elif (data_2 == ''):
                sys.stderr.write("Chyba, pokus o pracu s prazdnym retazcom\n")
                exit(58)
            else:
                
                self.parent.frames.set_var('string', data_0[:int(data_1)] + data_2[int(0)] + data_0[int(data_1)+1:], frame, name)
        else:
            sys.stderr.write("Chyba, instrukcia SETCHAR moze pracovat len s datovymi typmi int a string\n")
            exit(53)
            
    def TYPE(self):
        frame, name = self.args[0].value.split('@')
        data_type = self.type_fetch(self.args[1].type['type'], self.args[1].value)
        
        if(data_type is None):
            self.parent.frames.set_var('string', '', frame, name)
        else:
            self.parent.frames.set_var('string', data_type, frame, name)
      
    def LABEL(self):
        pass
    
    def JUMP(self):
        data_type_0, data_0 = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value)
        
        self.parent.instruction_exe = self.jump(data_type_0, data_0)
        self.parent.label_number = self.parent.instruction_exe
        self.order = self.parent.label_number
    
    def JUMPIFEQ(self):
        data_type_0, data_0 = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value) #label
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value) #symb1
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value) #symb2 
        if (data_type_1 == data_type_2 or data_type_1 == 'nil' or data_type_2 == 'nil'):
            if (data_1 == data_2):
                self.parent.instruction_exe = self.jump(data_type_0, data_0)
                self.parent.label_number = self.parent.instruction_exe
                self.order = self.parent.label_number
        else:
            sys.stderr.write("Chyba, instrukcia JUMPIFEQ moze pracovat len s datovymi typmi int, bool, string a nil\n")
            exit(53)
    
    def JUMPIFNEQ(self):
        data_type_0, data_0 = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value) #label
        data_type_1, data_1 = self.get_data_and_argument_type(self.args[1].type['type'], self.args[1].value) #symb1
        data_type_2, data_2 = self.get_data_and_argument_type(self.args[2].type['type'], self.args[2].value) #symb2 
        
        if (data_type_1 == data_type_2 or data_type_1 == 'nil' or data_type_2 == 'nil'):
            if (data_1 != data_2):
                self.parent.instruction_exe = self.jump(data_type_0, data_0)
                self.parent.label_number = self.parent.instruction_exe
                self.order = self.parent.label_number
        else:
            sys.stderr.write("Chyba, instrukcia JUMPIFEQ moze pracovat len s datovymi typmi int, bool, string a nil\n")
            exit(53)

    def CALL(self):
        data_type_0, data_0 = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value)
        self.parent.call_stack.append(self.parent.indx_instr)

        self.parent.instruction_exe = self.jump(data_type_0, data_0)
        self.parent.label_number = self.parent.instruction_exe
        self.order = self.parent.label_number
        
    def RETURN(self):
        if (len(self.parent.call_stack) == 0):
            sys.stderr.write("Chyba, pokus o pop operaciu na call stack-u\n")
            exit(56)
        else:
            self.parent.indx_instr = self.parent.call_stack.pop() 

    def EXIT(self):
            data_type_1, data_1 = self.get_data_and_argument_type(self.args[0].type['type'], self.args[0].value)   
        
            if (data_type_1 == 'int'):
                if (int(data_1) < 0 or int(data_1) > 49):
                    sys.stderr.write("Chyba, hodnota EXIT moze byt len v rozsahu 0-49\n")
                    exit(57)
                else:
                    exit(int(data_1))  
            else:
                sys.stderr.write("Chyba, instrukcia EXIT moze pracovat len s datovym typom int\n")
                exit(53)

    def BREAK(self):
        pass

    def jump(self, data_type, data):
        jump_label = data
        if (jump_label not in self.parent.labels):
            sys.stderr.write("Chyba, skok na neexistujuci label\n")
            exit(52)
        else:
            self.parent.indx_instr = self.parent.labels[jump_label]-1
            return self.parent.indx_instr 
      
    def type_fetch(self, data_type, data):
        if (data_type in ['int', 'bool', 'string', 'nil', 'type', 'label']):
            return data_type
        else:
            frame, value = data.split('@')
            arg_frame = self.parent.frames.get_right_frame(frame)
            if (arg_frame is None):
                sys.stderr.write("Chyba, pokus o pracu s neexistujucim ramcom\n")
                exit(55)
            if (value not in arg_frame):
                sys.stderr.write("Chyba, premenna neexistuje na ramci\n")
                exit(54)    
            else:           
                if (arg_frame[value]['type'] is None):
                    return None
                return arg_frame[value]['type']
                 
    def get_data_and_argument_type(self, data_type, data):
        if (data_type in ['int', 'bool', 'string', 'nil', 'type', 'label']):
            return data_type, data
        else:
            frame, value = data.split('@')
            arg_frame = self.parent.frames.get_right_frame(frame)
            if (arg_frame is None):
                sys.stderr.write("Chyba, pokus o pracu s neexistujucim ramcom\n")
                exit(55)
            if (value not in arg_frame):
                sys.stderr.write("Chyba, premenna neexistuje na ramci\n")
                sys.exit(54)    
            else:           
                if (arg_frame[value]['type'] is None or arg_frame[value]['value'] is None):
                    sys.stderr.write("Chyba, datovy typ alebo hodnota chybaju na ramci\n")
                    exit(56)
                return (arg_frame[value]['type'], arg_frame[value]['value'])
    
class argument:
    def __init__(self, type, value, order_num):
        self.type = type
        self.value = value  
        self.order_num = order_num