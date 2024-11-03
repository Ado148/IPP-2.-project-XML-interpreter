import sys
import instructions as instr

class Frames:
    def __init__(self):
        self.frame_stack = []
        self.global_frame = {}
        self.temp_frame = None
        self.is_tmp_defined = False # If temporary frame is defined, it is True, otherwise it is False                               
    
    def push_frame(self): # Insert temporary frame to the frame_stack array    
        if (self.is_tmp_defined):
            self.frame_stack.append(self.temp_frame)
            self.is_tmp_defined = False
        else:
            sys.stderr.write("Chyba, pokus o 'push' neexistujuceho ramca\n")
            exit(55)
       
    def pop_frame(self): # Pop temporary frame from the top of the frame_stack array
        if (len(self.frame_stack) <= 0):
            sys.stderr.write("Chyba, pokus o 'pop' neexistujuceho ramca\n")
            exit(55) 
        else:
            self.is_tmp_defined == True
            self.temp_frame = self.frame_stack.pop()    
            
    def get_right_frame(self, frame : str) -> dict:
        if (frame == 'GF'):
            return self.global_frame
        elif (frame == 'LF'):
            return self.get_LF()
        elif (frame == 'TF'):
            return self.get_TF()
        else:
           return None
                      
    def create_temporary_frame(self):
        self.temp_frame = {}
        self.is_tmp_defined = True
    
    def get_LF(self):
        return (self.frame_stack[-1] if len(self.frame_stack) > 0 else None)
    
    def get_TF(self):
        if (self.is_tmp_defined):
            return self.temp_frame 
        else:
            return None
    
    def set_var(self, type_of_var, value, frame, name): # Set value to the variable, type is e.g. var, value is a practical number, frame is e.g. GF, name is a name of the variable
        given_frame = self.get_right_frame(frame) # Get the right frame

        if (given_frame is None):
            sys.stderr.write("Chyba, pokus o pracu s neexistujucim ramcom\n")
            exit(55)
        if (name not in given_frame):
            sys.stderr.write("Chyba, pokus o pracu s neexistujucou premennou\n")
            exit(54)
        
        given_frame[name]['type'] = type_of_var
        given_frame[name]['value'] = value        