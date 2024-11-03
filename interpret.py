###
# IPP 2023 PROJECT: PART 2
#
# File: interpret.py
#
# Author: Adam Pap, xpapad11
#
###
import argparse
import xml.etree.ElementTree as ET
import os
import sys

from memory_model import Frames
from instructions import *

class Main_interpret:
    def __init__(self):
        self.instructions_list = []
        self.frames = Frames()
        self.labels = {}       
        self.stack_for_data = []
        self.call_stack = []
        
        self.instruction_exe = 0 #Inner counter of executed instructions for jumps 
        self.instruction_counter = 0
        self.label_number = 0
        
        self.source = ''
        self.input = ''
        
        self.__argument_parse() #Call argument parsing function
        self.start_interpreting() #Start interpreting
        self.execute_all() #Execute all instructions    
        
    def __argument_parse(self):
        argc = len(sys.argv) - 1 #Number of arguments

        parsed_arg = argparse.ArgumentParser(add_help=False)
        parsed_arg.add_argument("-h", "--help", help="Zobraz dany text", action='store_true')
        parsed_arg.add_argument("-s", "--source", help="Subor s IPPcode23 v XML formate.\n", metavar='FILE', type=str)
        parsed_arg.add_argument("-i", "--input", help="Subor pre interpretaciu zadaneho kodu (IPPcode23).", metavar='FILE', type=str)
        self.args = parsed_arg.parse_args()

        if (self.args.help):
            if (argc == 1):
                parsed_arg.print_help()
                exit(0)
            else:
                sys.stderr.write("S prepinacom --help nemoze byt dalsi prepinac.\n")
                exit(10)

        if (self.args.source):
            if (not os.path.isfile(self.args.source)):
                sys.stderr.write("Dany subor neexistuje.\n")
                exit(11) 
                
        if (self.args.input):
            if (not os.path.isfile(self.args.input)):
                sys.stderr.write("Dany subor neexistuje.\n")
                exit(11)
        
        if (self.args.source is None and self.args.input is None):
            sys.stderr.write("Program ocakava zadany bud --input=file parameter alebo --source=file.\n")
            exit(10)
            
    def XML_source_file(self): #Decide if we are reading from stdin or from the source file 
        if (self.args.source is None):
            return sys.stdin
        return self.args.source
    
    def start_interpreting(self):
        # Prepare various variables, arrays etc. for interpreting
        seen_orders = [] # Create empty array to chceck if order values does not duplicate
        
        
        # Open the files for reading which we got from argument parsing
        if (self.XML_source_file() is sys.stdin):   
            try:
                tree = ET.parse(sys.stdin)
            except: 
                sys.stderr.write("Standartny vstup obsahuje nekorektny XML\n")
                exit(31)      
        else:
            try: # Source file
                tree = ET.parse(self.args.source)
            except: 
                sys.stderr.write("Zdrojovy subor (Source file) obsahuje nekorektny XML\n")
                exit(31) 
              
        if (self.args.input): # Input file open
            sys.stdin = open(self.args.input, 'r')


        # Parsing the <program> atributes and check the version of language
        try:    
            root = tree.getroot()
            program_tag = root.tag
            IPP_language = root.attrib['language']
        except:
            sys.stderr.write("Nespravny XML format\n")
            exit(32)                                   
            
        if (IPP_language != 'IPPcode23'):
            sys.stderr.write("Nespravna verzia jazyka\n")
            exit(32)   
        elif(program_tag != 'program'):
            sys.stderr.write("Nespravny XML tag format\n")
            exit(32)
            
        for attrib in root.attrib: # Check if the atributes of the <program> tag are ok
            if (attrib not in ['language', 'description', 'name']): # for testing purposes 
                sys.stderr.write("Atribut tagu <program> je nespravne zapisany\n")
                exit(32)
        
        for child in root: # check for <instruction> tag and its correctness
            if (child.tag != 'instruction'):
                sys.stderr.write("Chyba v <instruction> tag\n")
                exit(32)  
            if ('opcode' not in child.attrib):
                sys.stderr.write("Chyba, tag <instruction> neobsahuje 'opcode'\n")
                exit(32)
            if ('order' not in child.attrib):
                sys.stderr.write("Chyba, tag <instruction> neobsahuje 'order'\n")
                exit(32)
            else:
                inner_instr_attrb = child.attrib 
                
                try: # Start chcecking if order of instruction is ok
                    instr_num = int(inner_instr_attrb['order'])
                except:
                    sys.stderr.write("Chyba, v <instruction> tag nebolo mozne identifikovat cislo z artributu 'order'\n")
                    exit(32) 
                if (instr_num <= 0):
                    sys.stderr.write("Chyba, v <instruction> tag su povolene len kladne cisla v atribute 'order'\n")
                    exit(32) 
                if (len(inner_instr_attrb) !=2): # Check if the atributes of the <instruction> tag are ok
                    sys.stderr.write("Chyba, tag <instruction> ma zly pocet atributov\n")
                    exit(32) 
                elif ('opcode' not in inner_instr_attrb):
                    sys.stderr.write("Chyba, tag <instruction> neobsahuje 'opcode'\n")
                    exit(32)
                elif ('order' not in inner_instr_attrb):
                    sys.stderr.write("Chyba, tag <instruction> neobsahuje 'order'\n")
                    exit(32) 

                if (inner_instr_attrb['opcode'].upper() in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']): # Check if the number of arguments is correct and if the syntax of instruction is ok
                    self.number_of_args(child, 0)
                elif (inner_instr_attrb['opcode'].upper() in ['DEFVAR', 'CALL', 'POPS', 'PUSHS', 'WRITE', 'LABEL', 'JUMP', 'EXIT', 'DPRINT']):
                    self.number_of_args(child, 1)
                elif (inner_instr_attrb['opcode'].upper() in ['NOT', 'MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'READ']):
                    self.number_of_args(child, 2)
                elif (inner_instr_attrb['opcode'].upper() in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR', 'JUMPIFEQ', 'JUMPIFNEQ']):
                    self.number_of_args(child, 3)
                else:
                    sys.stderr.write("Chyba, neznama instrukcia\n")
                    exit(32)   
                   
                if (instr_num in seen_orders): # Check if the order num already exists in the seen_orders array
                    sys.stderr.write("Chyba, opakujuce sa cislo 'order'\n")
                    exit(32)
                else:
                    seen_orders.append(instr_num)   
                    
                self.instruction_counter += 1    
                current_instr = instruction(inner_instr_attrb['opcode'], instr_num, self.frames, self) # Create new instruction object of current instruction
                
            for num, grandchild in enumerate(child, 1):
                if (inner_instr_attrb['opcode'] == 'LABEL'): # Check if the label is not already in the labels array
                    label_name = grandchild.text
                    if (label_name in self.labels):
                        sys.stderr.write("Chyba, opakujuci sa label\n")
                        exit(52)
                    else:
                        self.labels[label_name] = self.instruction_counter
   
                if (grandchild.tag not in['arg1', 'arg2', 'arg3']):
                    sys.stderr.write("Chyba nespravny tag\n")
                    exit(32)
                elif (num > 3):
                    sys.stderr.write("Chyba, ocakava sa len <arg1>, <arg2>, <arg3>\n")
                    exit(32)
                elif(grandchild.tag != 'arg' + str(num)):
                    xml_string = ET.tostring(root).decode() # Convert the xml to string in order to be able sort the args 
                    self.sort_args(xml_string)              
                elif (len(grandchild.attrib) != 1 or 'type' not in grandchild.attrib): # Check if the atributes of the <arg> tag are ok
                    sys.stderr.write("Chyba, ocakava sa <arg1-3 type=...>\n")
                    exit(32)
                elif (grandchild.attrib['type'] not in ['int', 'bool', 'string', 'nil', 'type', 'label', 'var']):
                    sys.stderr.write("Chyba, tag <arg> obsahuje nespravne typy\n")
                    exit(32)
                                           
                
                arg = argument(grandchild.attrib, grandchild.text.strip() if grandchild.text != None else grandchild.text, instr_num) # Create new argument object of the current argument
                current_instr.args.append(arg) # Add the argument to the current instruction
                
            self.instructions_list.append(current_instr) # Final instruction list    
        self.instructions_list.sort(key=lambda instr: instr.order) # Sort the instruction list by order of instruction



    def number_of_args(self, child, num_of_args): # Function to check number of arguments of the given instruction
        if (len(child) != num_of_args):
            sys.stderr.write("Chyba, nespravny pocet argumentov\n")
            exit(32)
            
    def sort_args(self, xml_string):
        root = ET.fromstring(xml_string)
        for instruction in root.findall('instruction'): # find all <instruction> tags
            all_args = instruction.findall('arg') # find all <arg> tags
            all_args.sort(key=lambda x: int(x.tag[3:])) # sort the <arg> tags by their number (x refers to <arg> and tag refers to the tag name) by strating at position 3                           
            for arg in all_args:                        # and remove the 'arg' part of the tag name
                instruction.remove(arg) # restructure the xml by removing the <arg> tags and append the sorted ones
                instruction.append(arg)
        return ET.tostring(root).decode()        

    def execute_all(self):
        self.indx_instr = 0
        
        while (self.indx_instr < len(self.instructions_list)):
            if(str(self.instructions_list[self.indx_instr].opcode) == 'None'):
                break
            
            self.instructions_list[self.indx_instr].execute()
            
            self.indx_instr += 1


def main_fun():
    xml_interpret = Main_interpret()

if __name__ == '__main__':
    main_fun()
