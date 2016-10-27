from EtherHis import *
from NumericStringParser import NumericStringParser

print "parser"

class Parser:
    def __init__(self):
        self.varTable= {}
        self.nsp = NumericStringParser()
        pass

    def run(self, filename):
        return self.parse(self.read_file(filename))
    
    def parse(self, lines):
        th = TransactionHistory()

        current_state = None
        
        for i in range(0, len(lines)):
            line = lines[i]
            if len(line)==0 or line[0] == '#' or line[0] == '\n':
                print "empty line or comment"
                continue
            
            c, j = getNextToken(line, 0)
            if c == "def":
                self.parse_def(line[j:])
                
            elif c == "state":
                pass
            elif c == "goto":
                pass
            elif c == "tr":
                self.parse_tr(line[j:])
                
            
            else:
                print "unrecognized command: " + str(len(line)) 
            
    def read_file(self,filename):
        f = open(filename, 'r')
        l = list(f)
        f.close()
        return l

    def parse_tr(self,line):
        #from
        c, j = getNextToken(line, 0)
        #to
        c, j = getNextToken(line, j)
        #value
        c, j = getNextToken(line, j)
        #gas
        c, j = getNextToken(line, j)
        #repeat
        c, j = getNextToken(line, j)
        #function

        #params

    def parse_goto(self,line):
        pass

    def parse_def(self, line):
        c , j = getNextToken(line, 0)
        varName = c

        #assuming a number
        print line[j:]
        value = self.nsp.eval(line[j:])

        print str(value)
        self.varTable[varName] = value
    
    def process_IR(self,string):
        pass
    
def is_al_num(string, index):
    if index == 0 or index == len(string):
        return False
    if string[index].isalnum() or string[index] == '_':
        return True
    return False

def replace_var(string, dic):
    print "replace var"
    for d in dic.keys():
        start_index = 0
        while True:
            i = string.find(d, start_index)
            if i==-1:
                break
            if not is_al_num(string,i-1) and not is_al_num(string,i + len(d)):
                string = string[:i] + str(dic[d]) + string[i+len(d):]
                start_index = i + len(str(dic[d]))
            else:
                start_index = i + 1
    return string

def main():
    dic = {"foo" : 123, "bar": 534.3, "baz" : -994, "foooa" : 223, "eebar":0}
    print dic
    string = "foo + baz ^ 2-eebar*foooa "
    string = replace_var(string, dic)
    print string

    nsp = NumericStringParser()
    print str(nsp.eval(string))

    p = Parser()
    p.run("Sample.txt")

def getNextToken(string, index):
    start = 0
    while True:
        if index >= len(string):
            return None, index
        if string[index] != " ":
            start = index
            #print "start = " + str(start)
            break
        index += 1
    while True:
        if index >= len(string) or string[index] == " ":
            #print string[start:index]
            return string[start:index].strip(), index
        index += 1

if __name__ == "__main__":
    main()
    

